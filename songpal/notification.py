"""Module for device notifications."""
import logging
from pprint import pformat as pf

import attr
from songpal.containers import (Power, SoftwareUpdateInfo,
                                make, convert_to_bool)

_LOGGER = logging.getLogger(__name__)


class Notification:
    """Wrapper for notifications.

    In order to listen for notifications, call `activate(callback)`
    with a coroutine to be called when a notification is received.
    """
    def __init__(self, endpoint, switch_method, payload):
        """Notification constructor.

        :param endpoint: Endpoint.
        :param switch_method: `Method` for switching this notification.
        :param payload: JSON data containing name and available versions.
        """
        self.endpoint = endpoint
        self.switch_method = switch_method
        self.versions = payload["versions"]
        self.name = payload["name"]
        self.version = max(x["version"] for x in self.versions if "version" in x)

        _LOGGER.debug("notification payload: %s", pf(payload))

    def asdict(self):
        """Return a dict containing the notification information."""
        return {"name": self.name, "version": self.version}

    async def activate(self, callback):
        """Start listening for this notification.

        Emits received notifications by calling the passed `callback`.
        """
        await self.switch_method({"enabled": [self.asdict()]}, _consumer=callback)

    def __repr__(self):
        return "<Notification %s, versions=%s, endpoint=%s>" % (
            self.name,
            self.versions,
            self.endpoint,
        )


class ChangeNotification:
    """Dummy base-class for notifications."""
    pass


@attr.s
class ConnectChange(ChangeNotification):
    connected = attr.ib()
    exception = attr.ib(default=None)

@attr.s
class PowerChange(ChangeNotification, Power):
    """Notification for power status change."""
    pass


@attr.s
class SoftwareUpdateChange(ChangeNotification):
    """Notification for available software updates."""
    make = classmethod(make)

    def _convert_if_available(x):
        if x is not None:
            return SoftwareUpdateInfo.make(**x[0])

    isUpdatable = attr.ib(convert=convert_to_bool)
    swInfo = attr.ib(convert=_convert_if_available)


@attr.s
class VolumeChange(ChangeNotification):
    """Notification for volume changes."""
    make = classmethod(make)

    mute = attr.ib(convert=lambda x: True if x == "on" else False)
    volume = attr.ib()


@attr.s
class SettingChange(ChangeNotification):
    """Notification for settings change."""
    make = classmethod(make)

    titleTextID = attr.ib()
    guideTextID = attr.ib()
    isAvailable = attr.ib()
    type = attr.ib()
    title = attr.ib()
    apiMappingUpdate = attr.ib()

    target = attr.ib()
    currentValue = attr.ib()

    def __attrs_post_init__(self):
        if self.type == 'directory':
            _LOGGER.debug("Got SettingChange for directory %s (see #36), "
                          "ignoring..", self.titleTextID)
            return
        if self.apiMappingUpdate is None:
            _LOGGER.warning("Got SettingChange for %s without "
                            "apiMappingUpdate, ignoring..", self.titleTextID)
            return
        self.currentValue = self.apiMappingUpdate["currentValue"]
        self.target = self.apiMappingUpdate["target"]

    def __str__(self):
        return "<SettingChange %s %s (%s): %s>" % (
            self.title,
            self.type,
            self.target,
            self.currentValue,
        )


@attr.s
class ContentChange(ChangeNotification):
    """This gets sent as a notification when the source changes."""
    make = classmethod(make)

    contentKind = attr.ib()
    service = attr.ib()
    source = attr.ib()
    uri = attr.ib()
    applicationName = attr.ib()

    @property
    def is_input(self):
        """Return if the change was related to input."""
        return self.contentKind == "input"


@attr.s
class NotificationChange(ChangeNotification):
    """Container for storing information about state of Notifications."""
    make = classmethod(make)

    enabled = attr.ib(convert=lambda x: [x["name"] for x in x])
    disabled = attr.ib(convert=lambda x: [x["name"] for x in x])

    def __str__(self):
        return "<NotificationChange enabled: %s disabled: %s>" % (
            ",".join(self.enabled),
            ",".join(self.disabled),
        )
