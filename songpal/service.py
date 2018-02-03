import json
import logging

import websockets

from songpal.method import Signature, Method
from songpal.notification import Notification

_LOGGER = logging.getLogger(__name__)


class Service:
    """Service presents an endpoint providing a set of methods."""
    def __init__(self, service, methods, notifications, idgen, debug=0):
        self.service = service
        self._methods = methods
        self.idgen = idgen
        self._protocols = []
        self._notifications = notifications
        self.debug = debug

    @staticmethod
    async def fetch_signatures(endpoint, version, idgen):
        async with websockets.connect(endpoint) as s:
            req = {"method": "getMethodTypes",
                   "params": [version],
                   "version": "1.0",
                   "id": next(idgen)}
            await s.send(json.dumps(req))
            res = await s.recv()
            return res

    @classmethod
    async def from_payload(cls, payload, endpoint, idgen, debug):
        service = payload["service"]
        methods = {}

        # 'protocol' contains information such as
        # xhrpost:jsonizer, websocket:jsonizer,
        # which are not handled here

        versions = set()
        for method in payload['apis']:
            # TODO we take only the first version here per method
            # should we prefer the newest version instead of that?
            versions.add(method["versions"][0]["version"])

        service_endpoint = "%s/%s" % (endpoint, service)

        signatures = {}
        for version in versions:
            try:
                sigs = await cls.fetch_signatures(service_endpoint,
                                                  version,
                                                  idgen)
                sigs = json.loads(sigs)

                for sig in sigs["results"]:
                    signatures[sig[0]] = Signature(*sig)
            except websockets.exceptions.InvalidHandshake as ex:
                if service != "guide":
                    _LOGGER.warning("Invalid handshake for %s: %s" % (service,
                                                                      ex))
            except json.JSONDecodeError as ex:
                _LOGGER.warning("Unable to parse json: %s" % sigs)

        for method in payload["apis"]:
            name = method["name"]
            if name in methods:
                raise Exception("Got duplicate %s for %s" % (name,
                                                             endpoint))
            if name not in signatures:
                _LOGGER.debug("Got no signature for %s on %s" % (name,
                                                                 endpoint))
                continue
            methods[name] = Method(service, service_endpoint,
                                   method, signatures[name],
                                   idgen, debug)

        notifications = []
        if "notifications" in payload:
            notifications = [Notification(service_endpoint,
                                          methods["switchNotifications"],
                                          notification)
                             for notification in payload["notifications"]]

        return cls(service, methods, notifications, idgen)

    def __getitem__(self, item):
        if item not in self._methods:
            raise Exception("%s does not contain method %s" % (self, item))
        return self._methods[item]

    @property
    def methods(self):
        return self._methods.values()

    @property
    def protocols(self):
        return self._protocols

    @property
    def notifications(self):
        return self._notifications

    async def listen_all_notifications(self, callback):
        """A helper to listen for all notifications by this service."""
        everything = [noti.asdict() for noti in self.notifications]
        await self._methods["switchNotifications"]({"enabled": everything},
                                                  _consumer=callback)

    def asdict(self):
        return {'methods': {m.name: m.asdict() for m in self.methods},
                'protocols': self.protocols,
                'notifications': {n.name: n.asdict()
                                  for n in self.notifications}}

    def __repr__(self):
        return "<Service %s: %s methods, %s protocols, %s notifications" % (
            self.service,
            len(self.methods),
            len(self.protocols),
            len(self.notifications))
