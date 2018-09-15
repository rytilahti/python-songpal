import asyncio
import json
import logging
from typing import List

import aiohttp

from songpal.common import ProtocolType, SongpalException
from songpal.method import Method, Signature
from songpal.notification import Notification

_LOGGER = logging.getLogger(__name__)


class Service:
    """Service presents an endpoint providing a set of methods."""
    def __init__(self, service,
                 methods, notifications, protocols,
                 idgen, debug=0):
        self.service = service
        self._methods = methods
        self.idgen = idgen
        self._protocols = protocols
        self._notifications = notifications
        self.debug = debug
        self.timeout = 2

    @staticmethod
    async def fetch_signatures(endpoint, version, protocol, idgen):
        async with aiohttp.ClientSession() as session:
            req = {"method": "getMethodTypes",
                   "params": [version],
                   "version": "1.0",
                   "id": next(idgen)}

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
        service = payload["service"]
        methods = {}

        if 'protocols' not in payload:
            raise SongpalException("Unable to find protocols from payload: %s" % payload)

        protocols = payload['protocols']
        _LOGGER.debug("Available protocols for %s: %s", service, protocols)
        if force_protocol and force_protocol.value in protocols:
            protocol = force_protocol
        elif 'websocket:jsonizer' in protocols:
            protocol = ProtocolType.WebSocket
        elif 'xhrpost:jsonizer' in protocols:
            protocol = ProtocolType.XHRPost
        else:
            raise SongpalException("No known protocols for %s, got: %s" % (
                service, protocols))
        _LOGGER.debug("Using protocol: %s" % protocol)

        versions = set()
        for method in payload['apis']:
            # TODO we take only the first version here per method
            # should we prefer the newest version instead of that?
            if len(method["versions"]) == 0:
                _LOGGER.warning("No versions found for %s", method)
            elif len(method["versions"]) > 1:
                _LOGGER.warning("More than on version for %s, "
                                "using the first one", method)
            versions.add(method["versions"][0]["version"])

        service_endpoint = "%s/%s" % (endpoint, service)

        signatures = {}
        for version in versions:
            sigs = await cls.fetch_signatures(service_endpoint,
                                              version,
                                              protocol,
                                              idgen)

            if debug > 1:
                _LOGGER.debug("Signatures: %s", sigs)
            if 'error' in sigs:
                _LOGGER.error("Got error when fetching sigs: %s", sigs['error'])
                return None

            for sig in sigs["results"]:
                signatures[sig[0]] = Signature(*sig)


        for method in payload["apis"]:
            name = method["name"]
            if name in methods:
                raise SongpalException("Got duplicate %s for %s" % (name,
                                                                    endpoint))
            if name not in signatures:
                _LOGGER.debug("Got no signature for %s on %s" % (name,
                                                                 endpoint))
                continue
            methods[name] = Method(service, service_endpoint,
                                   method, signatures[name],
                                   protocol,
                                   idgen, debug)

        notifications = []
        # TODO switchnotifications check is broken?
        if "notifications" in payload and "switchNotifications" in methods:
            notifications = [Notification(service_endpoint,
                                          methods["switchNotifications"],
                                          notification)
                             for notification in payload["notifications"]]

        return cls(service, methods, notifications, protocols, idgen)

    def __getitem__(self, item) -> Method:
        if item not in self._methods:
            raise SongpalException("%s does not contain method %s" % (self,
                                                                      item))
        return self._methods[item]

    @property
    def methods(self) -> List[Method]:
        return self._methods.values()

    @property
    def protocols(self):
        return self._protocols

    @property
    def notifications(self) -> List[Notification]:
        return self._notifications

    async def listen_all_notifications(self, callback):
        """A helper to listen for all notifications by this service."""
        everything = [noti.asdict() for noti in self.notifications]
        if len(everything) > 0:
            await self._methods["switchNotifications"]({"enabled": everything},
                                                       _consumer=callback)
        else:
            _LOGGER.debug("No notifications available for %s", self.service)

    def asdict(self):
        return {'methods': {m.name: m.asdict() for m in self.methods},
                'protocols': self.protocols,
                'notifications': {n.name: n.asdict()
                                  for n in self.notifications}}

    def __repr__(self):
        return "<Service %s: %s methods, %s notifications, protocols: %s" % (
            self.service,
            len(self.methods),
            len(self.notifications),
            self.protocols)
