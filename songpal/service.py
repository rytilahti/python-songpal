"""Service presentation for a single endpoint (e.g. audio or avContent)."""
import logging
from typing import List

import aiohttp

from songpal.common import ProtocolType, SongpalException
from songpal.method import Method, MethodSignature
from songpal.notification import (
    Notification,
    ConnectChange,
    ContentChange,
    NotificationChange,
    PowerChange,
    SettingChange,
    SoftwareUpdateChange,
    VolumeChange,
)

_LOGGER = logging.getLogger(__name__)


class Service:
    """Service presents an endpoint providing a set of methods."""

    def __init__(self, name, endpoint, protocol, idgen, debug=0):
        """Service constructor.

        Do not call this directly, but use :func:from_payload:
        """
        self.name = name
        self.endpoint = endpoint
        self.active_protocol = protocol
        self.idgen = idgen
        self._protocols = []
        self._notifications = []
        self.debug = debug
        self.timeout = 2
        self.listening = False

    @staticmethod
    async def fetch_signatures(endpoint, protocol, idgen):
        """Request available methods for the service."""
        async with aiohttp.ClientSession() as session:
            req = {
                "method": "getMethodTypes",
                "params": [""],
                "version": "1.0",
                "id": next(idgen),
            }

            if protocol == ProtocolType.WebSocket:
                async with session.ws_connect(endpoint, timeout=2) as s:
                    await s.send_json(req)
                    res = await s.receive_json()
                    return res
            else:
                res = await session.post(endpoint, json=req)
                json = await res.json()

                return json

    @classmethod
    async def from_payload(cls, payload, endpoint, idgen, debug, force_protocol=None):
        """Create Service object from a payload."""
        service_name = payload["service"]

        if "protocols" not in payload:
            raise SongpalException(
                "Unable to find protocols from payload: %s" % payload
            )

        protocols = payload["protocols"]
        _LOGGER.debug("Available protocols for %s: %s", service_name, protocols)
        if force_protocol and force_protocol.value in protocols:
            protocol = force_protocol
        elif "websocket:jsonizer" in protocols:
            protocol = ProtocolType.WebSocket
        elif "xhrpost:jsonizer" in protocols:
            protocol = ProtocolType.XHRPost
        else:
            raise SongpalException(
                "No known protocols for %s, got: %s" % (service_name, protocols)
            )
        _LOGGER.debug("Using protocol: %s" % protocol)

        service_endpoint = "%s/%s" % (endpoint, service_name)

        # creation here we want to pass the created service class to methods.
        service = cls(service_name, service_endpoint, protocol, idgen, debug)

        sigs = await cls.fetch_signatures(service_endpoint, protocol, idgen)

        if debug > 1:
            _LOGGER.debug("Signatures: %s", sigs)
        if "error" in sigs:
            _LOGGER.error("Got error when fetching sigs: %s", sigs["error"])
            return None

        methods = {}

        for sig in sigs["results"]:
            name = sig[0]
            parsed_sig = MethodSignature.from_payload(*sig)
            if name in methods:
                _LOGGER.debug(
                    "Got duplicate signature for %s, existing was %s. Keeping the existing one",
                    parsed_sig,
                    methods[name],
                )
            else:
                methods[name] = Method(service, parsed_sig, debug)

        service.methods = methods

        if "notifications" in payload and "switchNotifications" in methods:
            notifications = [
                Notification(
                    service_endpoint, methods["switchNotifications"], notification
                )
                for notification in payload["notifications"]
            ]
            service.notifications = notifications
            _LOGGER.debug("Got notifications: %s" % notifications)

        return service

    async def call_method(self, method, *args, **kwargs):
        """Call a method (internal).

        This is an internal implementation, which formats the parameters if necessary
         and chooses the preferred transport protocol.
         The return values are JSON objects.
        Use :func:__call__: provides external API leveraging this.
        """
        _LOGGER.debug(
            "%s got called with args (%s) kwargs (%s)" % (method.name, args, kwargs)
        )

        # Used for allowing keeping reading from the socket
        _consumer = None
        if "_consumer" in kwargs:
            if self.active_protocol != ProtocolType.WebSocket:
                raise SongpalException(
                    "Notifications are only supported over websockets"
                )
            _consumer = kwargs["_consumer"]
            del kwargs["_consumer"]

        if len(kwargs) == 0 and len(args) == 0:
            params = []  # params need to be empty array, if none is given
        elif len(kwargs) > 0:
            params = [kwargs]
        elif len(args) == 1 and args[0] is not None:
            params = [args[0]]
        else:
            params = []

        # TODO check for type correctness
        # TODO note parameters are not always necessary, see getPlaybackModeSettings
        # which has 'target' and 'uri' but works just fine without anything (wildcard)
        # if len(params) != len(self._inputs):
        #    _LOGGER.error("args: %s signature: %s" % (args,
        #                                              self.signature.input))
        #    raise Exception("Invalid number of inputs, wanted %s got %s / %s" % (
        #        len(self.signature.input), len(args), len(kwargs)))

        async with aiohttp.ClientSession() as session:
            req = {
                "method": method.name,
                "params": params,
                "version": method.version,
                "id": next(self.idgen),
            }
            if self.debug > 1:
                _LOGGER.debug(
                    "sending request: %s (proto: %s)", req, self.active_protocol
                )
            if self.active_protocol == ProtocolType.WebSocket:
                async with session.ws_connect(
                    self.endpoint, timeout=self.timeout, heartbeat=self.timeout * 5
                ) as s:
                    await s.send_json(req)
                    # If we have a consumer, we are going to loop forever while
                    # emiting the incoming payloads to e.g. notification handler.
                    if _consumer is not None:
                        self.listening = True
                        while self.listening:
                            res_raw = await s.receive_json()
                            res = self.wrap_notification(res_raw)
                            _LOGGER.debug("Got notification: %s", res)
                            if self.debug > 1:
                                _LOGGER.debug("Got notification raw: %s", res_raw)

                            await _consumer(res)

                    res = await s.receive_json()
                    return res
            else:
                res = await session.post(self.endpoint, json=req)
                return await res.json()

    def wrap_notification(self, data):
        """Convert notification JSON to a notification class."""
        if "method" in data:
            method = data["method"]
            params = data["params"]
            change = params[0]
            if method == "notifyPowerStatus":
                return PowerChange.make(**change)
            elif method == "notifyVolumeInformation":
                return VolumeChange.make(**change)
            elif method == "notifyPlayingContentInfo":
                return ContentChange.make(**change)
            elif method == "notifySettingsUpdate":
                return SettingChange.make(**change)
            elif method == "notifySWUpdateInfo":
                return SoftwareUpdateChange.make(**change)
            else:
                _LOGGER.warning(
                    "Got unknown notification type: %s - params: %s", method, params
                )
        elif "result" in data:
            result = data["result"][0]
            if "enabled" in result and "enabled" in result:
                return NotificationChange(**result)
        else:
            _LOGGER.warning("Unknown notification, returning raw: %s", data)
            return data

    def __getitem__(self, item) -> Method:
        """Return a method for the given name.

        Example:
            if "setPowerStatus" in system_service:
                system_service["setPowerStatus"](status="off")

        Raises SongpalException if the method does not exist.

        """
        if item not in self._methods:
            raise SongpalException("%s does not contain method %s" % (self, item))
        return self._methods[item]

    @property
    def methods(self) -> List[Method]:
        """List of methods implemented in this service."""
        return self._methods.values()

    @methods.setter
    def methods(self, methods):
        self._methods = methods

    @property
    def protocols(self):
        """Protocols supported by this service."""
        return self._protocols

    @protocols.setter
    def protocols(self, protocols):
        self._protocols = protocols

    @property
    def notifications(self) -> List[Notification]:
        """List of notifications exposed by this service."""
        return self._notifications

    @notifications.setter
    def notifications(self, notifications):
        self._notifications = notifications

    async def listen_all_notifications(self, callback):
        """Enable all exposed notifications.

        :param callback: Callback to call when a notification is received.
        """
        everything = [noti.asdict() for noti in self.notifications]
        if len(everything) > 0:
            await self._methods["switchNotifications"](
                {"enabled": everything}, _consumer=callback
            )
        else:
            _LOGGER.debug("No notifications available for %s", self.name)

    async def stop_listen_notifications(self):
        _LOGGER.debug("Stop listening on %s" % self.name)
        self.listening = False

    def asdict(self):
        """Return dict presentation of this service.

        Useful for dumping the device information into JSON.
        """
        return {
            "methods": {m.name: m.asdict() for m in self.methods},
            "protocols": self.protocols,
            "notifications": {n.name: n.asdict() for n in self.notifications},
        }

    def __repr__(self):
        return (
            "<Service %s: %s methods, %s notifications, protocols: %s (active: %s)"
            % (
                self.name,
                len(self.methods),
                len(self.notifications),
                self.protocols,
                self.active_protocol,
            )
        )
