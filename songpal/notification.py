"""Module for device notifications."""
import logging
from collections.abc import Awaitable
from pprint import pformat as pf
from typing import Callable, List

import attr

from songpal.containers import PlayInfo, Power, SoftwareUpdateInfo, make

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
        return "<Notification {}, versions={}, endpoint={}>".format(
            self.name,
            self.versions,
            self.endpoint,
        )


class ChangeNotification:
    """Dummy base-class for notifications."""


# A type-annotation for change notification callbacks
NotificationCallback = Callable[[ChangeNotification], Awaitable[None]]


@attr.s
class ConnectChange(ChangeNotification):
    """Notification for connection status.

    This is used to inform listeners if the device connectivity drops.
    """

    connected = attr.ib()
    exception = attr.ib(default=None)


@attr.s
class PowerChange(ChangeNotification, Power):
    """Notification for power status change."""


@attr.s
class ZoneActivatedChange(ChangeNotification):
    """Notification for zone power status change."""

    make = classmethod(make)

    def _convert_bool(x) -> bool:
        return x == "active"

    active = attr.ib(converter=_convert_bool)
    connection = attr.ib()
    label = attr.ib()
    uri = attr.ib()


@attr.s
class SoftwareUpdateChange(ChangeNotification, SoftwareUpdateInfo):
    """Notification for available software updates."""


@attr.s
class VolumeChange(ChangeNotification):
    """Notification for volume changes."""

    make = classmethod(make)

    def _convert_bool(x) -> bool:
        return x == "on"

    mute = attr.ib(converter=_convert_bool)
    volume = attr.ib()
    output = attr.ib()


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
        if self.type == "directory":
            _LOGGER.debug(
                "Got SettingChange for directory %s (see #36), " "ignoring..",
                self.titleTextID,
            )
            return
        if self.apiMappingUpdate is None:
            _LOGGER.warning(
                "Got SettingChange for %s without " "apiMappingUpdate, ignoring..",
                self.titleTextID,
            )
            return
        self.currentValue = self.apiMappingUpdate["currentValue"]
        self.target = self.apiMappingUpdate["target"]

    def __str__(self):
        return "<SettingChange {} {} ({}): {}>".format(
            self.title,
            self.type,
            self.target,
            self.currentValue,
        )


@attr.s
class ContentChange(ChangeNotification, PlayInfo):
    """This gets sent as a notification when the source changes."""

    make = classmethod(make)

    kind = attr.ib()
    """Used by newer devices, continue to access via `contentKind`"""

    def __attrs_post_init__(self):
        if self.contentKind is None:
            self.contentKind = self.kind

    @property
    def is_input(self):
        """Return if the change was related to input."""
        return self.contentKind == "input"


@attr.s
class NotificationChange(ChangeNotification):
    """Container for storing information about state of Notifications."""

    make = classmethod(make)

    def _extract_notification_names(x) -> List[str]:
        return [x["name"] for x in x]  # type: ignore

    enabled = attr.ib(converter=_extract_notification_names)
    disabled = attr.ib(converter=_extract_notification_names)

    def __str__(self):
        return "<NotificationChange enabled: {} disabled: {}>".format(
            ",".join(self.enabled),
            ",".join(self.disabled),
        )


@attr.s
class PlaybackFunctionChange(ChangeNotification):
    """Container for storing playback function changes."""

    make = classmethod(make)

    functions = attr.ib()
    uri = attr.ib()


@attr.s
class StorageChange(ChangeNotification):
    """Container for storing storage changes."""

    make = classmethod(make)

    isAvailable = attr.ib()
    mounted = attr.ib()
    uri = attr.ib()
