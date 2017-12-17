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
                'endpoint': self.endpoint,
                'versions': self.versions,
                'version': self.version}

    def activate(self):
        # notifyPowerStatus, notifySWUpdateInfo,
        # notifySettingsUpdate, notifyStorageStatus
        # {"method": "switchNotifications",
        # "params": [{"enabled": [{"name": name, "version": version}]}]}
        pass

    def __repr__(self):
        return "<Notification %s, versions=%s, endpoint=%s>" % (self.name,
                                                                self.versions,
                                                                self.endpoint)
