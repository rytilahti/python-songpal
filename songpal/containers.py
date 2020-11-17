"""Data containers for Songpal."""
import logging
from datetime import timedelta
from typing import List, Optional, Union

import attr

from songpal import SongpalException

_LOGGER = logging.getLogger(__name__)


def make(cls, **kwargs):
    """Create a container.

    Reports extra keys as well as missing ones.
    Thanks to habnabit for the idea!
    """
    cls_attrs = {f.name: f for f in attr.fields(cls)}

    unknown = {k: v for k, v in kwargs.items() if k not in cls_attrs}
    if len(unknown) > 0:
        _LOGGER.debug(
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


def convert_to_bool(x) -> bool:
    """Convert string 'true' to bool."""
    return x == "true"


def convert_is_active(x) -> bool:
    """Convert string 'active' to bool."""
    return True if x == "active" else False


def convert_title(x) -> str:
    """Trim trailing characters on the title"""
    return x.strip()


@attr.s
class Scheme:
    """Input scheme container."""

    make = classmethod(make)

    scheme = attr.ib()  # type: str


@attr.s
class PlaybackFunction:
    """Playback function."""

    make = classmethod(make)

    function = attr.ib()


@attr.s
class SupportedFunctions:
    """Container for supported playback functions."""

    make = classmethod(make)

    def _convert_playback_functions(x) -> List[PlaybackFunction]:
        return [PlaybackFunction.make(**y) for y in x]  # type: ignore

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

    def _make(x) -> StateInfo:
        return StateInfo.make(**x)  # type: ignore

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

    maxVolume = attr.ib()
    minVolume = attr.ib()
    mute = attr.ib()
    output = attr.ib()
    step = attr.ib()
    volume = attr.ib()

    @property
    def is_muted(self):
        """Return True if volume is muted."""
        return self.mute == "on" or self.mute is True

    def __str__(self):
        if self.output and self.output.rfind("=") > 0:
            s = "Zone %s Volume: %s/%s" % (
                self.output[self.output.rfind("=") + 1 :],
                self.volume,
                self.maxVolume,
            )
        else:
            s = "Volume: %s/%s" % (self.volume, self.maxVolume)
        if self.is_muted:
            s += " (muted)"
        return s

    async def set_mute(self, activate: bool):
        """Set mute on/off."""
        raise NotImplementedError

    async def toggle_mute(self):
        """Toggle mute."""
        raise NotImplementedError

    async def set_volume(self, volume: Union[str, int]):
        """Set volume level."""
        raise NotImplementedError


@attr.s
class VolumeControlSongpal(Volume):
    services = attr.ib(repr=False)

    async def set_mute(self, activate: bool):
        enabled = "off"
        if activate:
            enabled = "on"

        return await self.services["audio"]["setAudioMute"](
            mute=enabled, output=self.output
        )

    async def toggle_mute(self):
        return await self.services["audio"]["setAudioMute"](
            mute="toggle", output=self.output
        )

    async def set_volume(self, volume: Union[str, int]):
        return await self.services["audio"]["setAudioVolume"](
            volume=str(volume), output=self.output
        )


@attr.s
class VolumeControlUpnp(Volume):

    renderingControl = attr.ib(default=None)

    async def set_mute(self, activate: bool):
        """Set mute on/off."""

        return await self.renderingControl.action("SetMute").async_call(
            InstanceID=0, Channel="Master", DesiredMute=activate
        )

    async def toggle_mute(self):
        mute_result = await self.renderingControl.action("GetMute").async_call(
            InstanceID=0, Channel="Master"
        )
        return self.set_mute(not mute_result["CurrentMute"])

    async def set_volume(self, volume: Union[str, int]):
        if isinstance(volume, str):
            if "+" in volume or "-" in volume:
                raise SongpalException(
                    "Setting relative volume not supported with UPnP"
                )
            desired_volume = int(volume)
        elif isinstance(volume, int):
            desired_volume = volume
        else:
            raise SongpalException("Invalid volume %s" % volume)

        return await self.renderingControl.action("SetVolume").async_call(
            InstanceID=0, Channel="Master", DesiredVolume=desired_volume
        )


@attr.s
class Power:
    """Information about power status.

    This implements __bool__() for easy checking if the device is turned on or not.
    """

    make = classmethod(make)

    status = attr.ib(converter=convert_is_active)
    standbyDetail = attr.ib()

    def __bool__(self):
        return self.status

    def __str__(self):
        if self.status:
            return "Power on"
        else:
            return "Power off"


@attr.s
class Zone:
    """Zone information."""

    make = classmethod(make)

    meta = attr.ib()
    connection = attr.ib()
    title = attr.ib(converter=convert_title)
    uri = attr.ib()

    services = attr.ib(repr=False)
    active = attr.ib(converter=convert_is_active)
    label = attr.ib()
    iconUrl = attr.ib()

    def __str__(self):
        s = "%s (uri: %s)" % (self.title, self.uri)
        if self.active:
            s += " (active)"
        return s

    async def activate(self, activate):
        """Activate this zone."""
        return await self.services["avContent"]["setActiveTerminal"](
            active="active" if activate else "inactive", uri=self.uri
        )


@attr.s
class Input:
    """Input information."""

    make = classmethod(make)

    title = attr.ib(converter=convert_title)
    uri = attr.ib()

    active = attr.ib(converter=convert_is_active)
    label = attr.ib()
    iconUrl = attr.ib()
    outputs = attr.ib(default=attr.Factory(list))

    def __str__(self):
        s = "%s (uri: %s)" % (self.title, self.uri)
        if self.active:
            s += " (active)"
        return s

    async def activate(self, output: Zone = None):
        """Activate this input."""
        raise NotImplementedError


@attr.s
class InputControlSongpal(Input):
    meta = attr.ib(default=None)
    connection = attr.ib(default=None)
    services = attr.ib(default=None, repr=False)

    def __str__(self):
        s = "%s (uri: %s)" % (self.title, self.uri)
        if self.active:
            s += " (active)"
        return s

    async def activate(self, output: Zone = None):
        output_uri = output.uri if output else ""
        return await self.services["avContent"]["setPlayContent"](
            uri=self.uri, output=output_uri
        )


@attr.s
class InputControlUpnp(Input):

    avTransport = attr.ib(default=None)
    uriMetadata = attr.ib(default=None)

    async def activate(self, output: Zone = None):
        result = await self.avTransport.action("SetAVTransportURI").async_call(
            InstanceID=0, CurrentURI=self.uri, CurrentURIMetaData=self.uriMetadata
        )

        try:
            # Attempt to play as the songpal app is doing after changing input,
            # sometimes needed so that input emits sound
            await self.avTransport.action("Play").async_call(InstanceID=0, Speed="1")
        except Exception:
            # Play action can cause 500 error in certain cases
            pass

        return result


@attr.s
class Storage:
    """Storage information."""

    make = classmethod(make)

    def _make(x) -> bool:
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

    def _convert_if_available(x) -> Optional[List["SettingsEntry"]]:
        if x is not None:
            return [SettingsEntry.make(**y) for y in x]  # type: ignore

        return None

    def _convert_if_available_mapping(x) -> Optional[ApiMapping]:
        if x is not None:
            return ApiMapping.make(**x)  # type: ignore

        return None

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

    def _create_candidates(x) -> List[SettingCandidate]:
        if x is not None:
            return [SettingCandidate.make(**y) for y in x]  # type: ignore

        return []

    currentValue = attr.ib()
    target = attr.ib()
    type = attr.ib()
    candidate = attr.ib(converter=_create_candidates)
    isAvailable = attr.ib()
    title = attr.ib()
    titleTextID = attr.ib()
    deviceUIInfo = attr.ib()
    uri = attr.ib()
