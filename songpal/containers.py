"""Data containers for Songpal."""
from datetime import timedelta
import logging
from typing import List  # noqa: F401

import attr

_LOGGER = logging.getLogger(__name__)


def make(cls, **kwargs):
    """Create a container.

    Reports extra keys as well as missing ones.
    Thanks to habnabit for the idea!
    """
    cls_attrs = {f.name: f for f in attr.fields(cls)}

    unknown = {k: v for k, v in kwargs.items() if k not in cls_attrs}
    if len(unknown) > 0:
        _LOGGER.warning(
            "Got unknowns for %s: %s - please create an issue!", cls.__name__, unknown
        )

    missing = [k for k in cls_attrs if k not in kwargs]

    data = {k: v for k, v in kwargs.items() if k in cls_attrs}

    # initialize missing values to avoid passing default=None
    # for the attrs attribute definitions
    for m in missing:
        default = cls_attrs[m].default
        if isinstance(default, attr.Factory):
            if not default.takes_self:
                data[m] = default.factory()
            else:
                raise NotImplementedError
        else:
            _LOGGER.debug("Missing key %s with no default for %s", m, cls.__name__)
            data[m] = None

    # initialize and store raw data for debug purposes
    inst = cls(**data)
    setattr(inst, "raw", kwargs)

    return inst


def convert_to_bool(x):
    """Convert string 'true' to bool."""
    return x == "true"


@attr.s
class Scheme:
    """Input scheme container."""
    make = classmethod(make)

    scheme = attr.ib()


@attr.s
class PlaybackFunction:
    """Playback function."""
    make = classmethod(make)

    function = attr.ib()


@attr.s
class SupportedFunctions:
    """Container for supported playback functions."""
    make = classmethod(make)

    def _convert_playback_functions(x):
        return [PlaybackFunction.make(**y) for y in x]

    uri = attr.ib()
    functions = attr.ib(converter=_convert_playback_functions)


@attr.s
class ContentInfo:
    """Information about available contents."""
    make = classmethod(make)

    capability = attr.ib()
    count = attr.ib()


@attr.s
class Content:
    """Content infrormation."""
    make = classmethod(make)

    isBrowsable = attr.ib()
    uri = attr.ib()
    contentKind = attr.ib()

    isPlayable = attr.ib()
    index = attr.ib()
    title = attr.ib()  # no idea why this would be missing..
    folderNo = attr.ib()  # files do not have this
    fileNo = attr.ib()  # folders do not have this
    parentUri = attr.ib()  # toplevel has no parents

    fileSizeByte = attr.ib()  # dirs do not have this
    createdTime = attr.ib()

    broadcastFreqBand = attr.ib()
    broadcastFreq = attr.ib()

    def __str__(self):
        return "%s (%s, kind: %s)" % (self.title, self.uri, self.contentKind)


@attr.s
class StateInfo:
    """Playback state."""
    make = classmethod(make)

    state = attr.ib()
    supplement = attr.ib()


@attr.s
class PlayInfo:
    """Information about played content.

    This is only tested on music files,
    the outs for the method call is much, much larger
    """
    make = classmethod(make)

    def _make(x):
        return StateInfo.make(**x)

    stateInfo = attr.ib(converter=_make)
    contentKind = attr.ib()
    uri = attr.ib()
    output = attr.ib()

    # only available when being played
    service = attr.ib()
    artist = attr.ib()
    albumName = attr.ib()
    title = attr.ib()
    durationMsec = attr.ib()
    mediaType = attr.ib()
    parentUri = attr.ib()
    positionMsec = attr.ib()
    repeatType = attr.ib()
    source = attr.ib()

    @property
    def is_idle(self):
        """Return if content is being played."""
        return self.title is None

    @property
    def state(self):
        """Return playback state."""
        return self.stateInfo.state

    @property
    def duration(self):
        """Return total media duration."""
        if self.durationMsec is not None:
            return timedelta(milliseconds=self.durationMsec)

    @property
    def position(self):
        """Return current media position."""
        if self.positionMsec is not None:
            return timedelta(milliseconds=self.positionMsec)

    def __str__(self):
        return "%s (%s/%s), state %s" % (
            self.title,
            self.position,
            self.duration,
            self.state,
        )


@attr.s
class InterfaceInfo:
    """Information about the product."""
    make = classmethod(make)

    productName = attr.ib()
    modelName = attr.ib()
    productCategory = attr.ib()
    interfaceVersion = attr.ib()
    serverName = attr.ib()


@attr.s
class Sysinfo:
    """System information."""
    make = classmethod(make)

    bdAddr = attr.ib()
    macAddr = attr.ib()
    version = attr.ib()
    wirelessMacAddr = attr.ib()
    bssid = attr.ib()
    ssid = attr.ib()
    bleID = attr.ib()


@attr.s
class SoftwareUpdateInfo:
    """Software update information."""
    make = classmethod(make)

    isUpdatable = attr.ib(converter=convert_to_bool)
    swInfo = attr.ib()
    estimatedTimeSec = attr.ib()
    target = attr.ib()
    updatableVersion = attr.ib()
    forcedUpdate = attr.ib(converter=convert_to_bool)


@attr.s
class Source:
    """Source information."""
    make = classmethod(make)

    title = attr.ib()
    source = attr.ib()

    iconUrl = attr.ib()
    isBrowsable = attr.ib()
    isPlayable = attr.ib()
    meta = attr.ib()
    playAction = attr.ib()
    outputs = attr.ib()

    def __str__(self):
        s = "%s (%s)" % (self.title, self.source)
        if self.outputs is not None:
            s += " - outs: %s" % self.outputs
        return s


@attr.s
class Volume:
    """Volume information."""
    make = classmethod(make)

    services = attr.ib(repr=False)
    maxVolume = attr.ib()
    minVolume = attr.ib()
    mute = attr.ib()
    output = attr.ib()
    step = attr.ib()
    volume = attr.ib()

    @property
    def is_muted(self):
        """Return True if volume is muted."""
        return self.mute == "on"

    def __str__(self):
        s = "Volume: %s/%s" % (self.volume, self.maxVolume)
        if self.is_muted:
            s += " (muted)"
        return s

    async def set_mute(self, activate: bool):
        """Set mute on/off."""
        enabled = "off"
        if activate:
            enabled = "on"

        return await self.services["audio"]["setAudioMute"](
            mute=enabled, output=self.output
        )

    async def toggle_mute(self):
        """Toggle mute."""
        return await self.services["audio"]["setAudioMute"](
            mute="toggle", output=self.output
        )

    async def set_volume(self, volume: int):
        """Set volume level."""
        return await self.services["audio"]["setAudioVolume"](
            volume=str(volume), output=self.output
        )


@attr.s
class Power:
    """Information about power status.

    This implements __bool__() for easy checking if the device is turned on or not.
    """
    make = classmethod(make)

    def _make(x):
        return True if x == "active" else False

    status = attr.ib(converter=_make)
    standbyDetail = attr.ib()

    def __bool__(self):
        return self.status

    def __str__(self):
        if self.status:
            return "Power on"
        else:
            return "Power off"


@attr.s
class Input:
    """Input information."""
    make = classmethod(make)

    def _convert_title(x):
        return x.strip()

    def _convert_is_active(x):
        return True if x == "active" else False

    meta = attr.ib()
    connection = attr.ib()
    title = attr.ib(converter=_convert_title)
    uri = attr.ib()

    services = attr.ib(repr=False)
    active = attr.ib(converter=_convert_is_active)
    label = attr.ib()
    iconUrl = attr.ib()
    outputs = attr.ib(default=attr.Factory(list))

    def __str__(self):
        s = "%s (uri: %s)" % (self.title, self.uri)
        if self.active:
            s += " (active)"
        return s

    async def activate(self):
        """Activate this input."""
        return await self.services["avContent"]["setPlayContent"](uri=self.uri)

@attr.s
class Zone:
    """Zone information."""
    make = classmethod(make)

    def _convert_title(x):
        return x.strip()

    def _convert_is_active(x):
        return True if x == "active" else False

    meta = attr.ib()
    connection = attr.ib()
    title = attr.ib(converter=_convert_title)
    uri = attr.ib()

    services = attr.ib(repr=False)
    active = attr.ib(converter=_convert_is_active)
    label = attr.ib()
    iconUrl = attr.ib()

    def __str__(self):
        s = "%s (uri: %s)" % (self.title, self.uri)
        if self.active:
            s += " (active)"
        return s

    async def activate(self, activate):
        """Activate this zone."""
        return await self.services["avContent"]["setActiveTerminal"](active=activate, uri=self.uri)


@attr.s
class Storage:
    """Storage information."""
    make = classmethod(make)

    def _make(x):
        return True if x == "mounted" else False

    deviceName = attr.ib()
    uri = attr.ib()
    volumeLabel = attr.ib()

    freeCapacityMB = attr.ib()
    systemAreaCapacityMB = attr.ib()
    wholeCapacityMB = attr.ib()

    formattable = attr.ib()
    formatting = attr.ib()

    isAvailable = attr.ib(converter=convert_to_bool)
    mounted = attr.ib(converter=_make)
    permission = attr.ib()
    position = attr.ib()

    def __str__(self):
        return "%s (%s) in %s (%s/%s free), available: %s, mounted: %s" % (
            self.deviceName,
            self.uri,
            self.position,
            self.freeCapacityMB,
            self.wholeCapacityMB,
            self.isAvailable,
            self.mounted,
        )


@attr.s
class ApiMapping:
    """API mapping for some setting setters/getters."""
    make = classmethod(make)

    service = attr.ib()
    getApi = attr.ib()

    setApi = attr.ib()
    target = attr.ib()
    targetSuppl = attr.ib()


@attr.s
class SettingsEntry:
    """Presentation of a single setting."""
    make = classmethod(make)

    isAvailable = attr.ib()
    type = attr.ib()

    def _convert_if_available(x):
        if x is not None:
            return [SettingsEntry.make(**y) for y in x]

    def _convert_if_available_mapping(x):
        if x is not None:
            return ApiMapping.make(**x)

    async def get_value(self, dev):
        """Return current value for this setting."""
        res = await dev.get_setting(
            self.apiMapping.service,
            self.apiMapping.getApi["name"],
            self.apiMapping.target,
        )
        return Setting.make(**res.pop())

    @property
    def is_directory(self):
        """Return True if the setting is a directory."""
        return self.type == "directory"

    apiMapping = attr.ib(converter=_convert_if_available_mapping, repr=False)
    settings = attr.ib(converter=_convert_if_available)
    title = attr.ib()
    titleTextID = attr.ib()
    usage = attr.ib()
    deviceUIInfo = attr.ib()

    def __str__(self):
        return "%s (%s, %s)" % (self.title, self.titleTextID, self.type)


@attr.s
class SettingCandidate:
    """Representation of a setting candidate aka. option."""
    make = classmethod(make)

    title = attr.ib()
    value = attr.ib()
    isAvailable = attr.ib()
    min = attr.ib()
    max = attr.ib()
    step = attr.ib()
    titleTextID = attr.ib()


@attr.s
class Setting:
    """Representation of a setting.

    Use `candidate` to access the potential values.
    """
    make = classmethod(make)

    def _create_candidates(x):
        if x is not None:
            return [SettingCandidate.make(**y) for y in x]

        return []

    currentValue = attr.ib()
    target = attr.ib()
    type = attr.ib()
    candidate = attr.ib(converter=_create_candidates)  # type: List[SettingCandidate]
    isAvailable = attr.ib()
    title = attr.ib()
    titleTextID = attr.ib()
    deviceUIInfo = attr.ib()
    uri = attr.ib()
