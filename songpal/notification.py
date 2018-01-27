import websockets
import logging
import json

_LOGGER = logging.getLogger(__name__)

class Notification:
    """Wrapper for notifications, currently unused"""
    def __init__(self, endpoint, payload):
        self.endpoint = endpoint
        self.versions = payload["versions"]
        self.name = payload["name"]
        self.version = max([x['version']
                            for x in self.versions
                            if 'version' in x])

    def asdict(self):
        return {'name': self.name,
                #'endpoint': self.endpoint,
                #'versions': self.versions,
                'version': self.version}

    async def activate(self):
        # notifyPowerStatus, notifySWUpdateInfo,
        # notifySettingsUpdate, notifyStorageStatus
        # {"method": "switchNotifications",
        # "params": [{"enabled": [{"name": name, "version": version}]}]}
        async with websockets.connect(self.endpoint, timeout=5) as s:
            req = {"method": "switchNotifications",
                   "params": [{"enabled": [],
                               "disabled": []}],
                   "version": self.version,
                   "id": 1}
            json_req = json.dumps(req)
            print("sending %s" % json_req)
            await s.send(json_req)
            res = await s.recv()
            print("received subscription: %s" % res)
            req = {"method": "switchNotifications",
                   "params": [{"enabled": [self.asdict()],
                               "disabled": []}],
                   "version": self.version,
                   "id": 2}
            json_req = json.dumps(req)
            print("sending %s" % json_req)
            await s.send(json_req)
            while True:
                _LOGGER.info("going to wait for input")
                res = await s.recv()
                _LOGGER.info("got from loop: %s" % res)

    def __repr__(self):
        return "<Notification %s, versions=%s, endpoint=%s>" % (self.name,
                                                                self.versions,
                                                                self.endpoint)
