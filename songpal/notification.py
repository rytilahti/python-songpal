import logging
from pprint import pformat as pf

_LOGGER = logging.getLogger(__name__)

class Notification:
    """Wrapper for notifications.

    In order to listen for notifications, call `activate(callback)`
    with a coroutine to be called when a notification is received.
    """
    def __init__(self, endpoint, switch_method, payload):
        self.endpoint = endpoint
        self.switch_method = switch_method
        self.versions = payload["versions"]
        self.name = payload["name"]
        self.version = max([x['version']
                            for x in self.versions
                            if 'version' in x])

        _LOGGER.debug("notification payload: %s", pf(payload))

    def asdict(self):
        return {'name': self.name,
                'version': self.version}

    async def activate(self, callback):
        """Start listening for this notification.

        Emits received notifications by calling the passed `callback`.
        """
        await self.switch_method({"enabled": [self.asdict()]}, _consumer=callback)

    def __repr__(self):
        return "<Notification %s, versions=%s, endpoint=%s>" % (self.name,
                                                                self.versions,
                                                                self.endpoint)
