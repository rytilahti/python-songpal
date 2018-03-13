from datetime import timedelta
import logging
from typing import List
import attr


_LOGGER = logging.getLogger(__name__)


def make(cls, **kwargs):
    """A wrapper for constructing containers.

    Reports extra keys as well as missing ones.
    Thanks to habnabit for the idea!
    """
    cls_attrs = {f.name for f in attr.fields(cls)}

    unknown = {k: v for k, v in kwargs.items() if k not in cls_attrs}
    if len(unknown) > 0:
        _LOGGER.warning("Got unknowns for %s: %s - please create an issue!",
                      cls.__name__, unknown)

    missing = [k for k in cls_attrs if k not in kwargs]
    if len(missing) > 0:
        _LOGGER.debug("Missing keys for %s: %s", cls.__name__, missing)

    data = {k: v for k, v in kwargs.items() if k in cls_attrs}

    # initialize missing values to avoid passing default=None
    # for the attrs attribute definitions
    for m in missing:
        data[m] = None

    # initialize and store raw data for debug purposes
    inst = cls(**data)
    setattr(inst, 'raw', kwargs)

    return inst


class ChangeNotification:
    """Dummy base-class for notifications."""
    pass

@attr.s
class Scheme:
    make = classmethod(make)

    scheme = attr.ib()


@attr.s
class PlaybackFunction:
    make = classmethod(make)

    function = attr.ib()


@attr.s
class SupportedFunctions:
    make = classmethod(make)

    uri = attr.ib()
    functions = attr.ib(convert=lambda x: [PlaybackFunction.make(y) for y in x])


@attr.s
class ContentInfo:
    make = classmethod(make)

    capability = attr.ib()
    count = attr.ib()


@attr.s
class Content:
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

    def __str__(self):
        return "%s (%s, kind: %s)" % (self.title, self.uri, self.contentKind)


@attr.s
class StateInfo:
    make = classmethod(make)

    state = attr.ib()
    supplement = attr.ib()


@attr.s
class PlayInfo:
    """This is only tested on music files,
    the outs for the method call is much, much larger"""
    make = classmethod(make)

    stateInfo = attr.ib(convert=lambda x: StateInfo(**x))
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
        return self.title is None

    @property
    def state(self):
        return self.stateInfo.state

    @property
    def duration(self):
        return timedelta(milliseconds=self.durationMsec)

    @property
    def position(self):
        return timedelta(milliseconds=self.positionMsec)

    def __str__(self):
        return "%s (%s/%s), state %s" % (self.title,
                                         self.position,
                                         self.duration,
                                         self.state)


@attr.s
class InterfaceInfo:
    make = classmethod(make)

    productName = attr.ib()
    modelName = attr.ib()
    productCategory = attr.ib()
    interfaceVersion = attr.ib()
    serverName = attr.ib()


@attr.s
class Sysinfo:
    make = classmethod(make)

    bdAddr = attr.ib()
    macAddr = attr.ib()
    version = attr.ib()
    wirelessMacAddr = attr.ib()
    bssid = attr.ib()
    ssid = attr.ib()


def convert_bool(x):
    return x == 'true'


@attr.s
class SoftwareUpdateInfo:
    make = classmethod(make)

    estimatedTimeSec = attr.ib()
    target = attr.ib()
    updatableVersion = attr.ib()
    forcedUpdate = attr.ib(convert=convert_bool)


@attr.s
class SoftwareUpdateChange(ChangeNotification):
    make = classmethod(make)

    def convert_if_available(x):
        if x is not None:
            return SoftwareUpdateInfo.make(**x[0])

    isUpdatable = attr.ib(convert=convert_bool)
    swInfo = attr.ib(convert=convert_if_available)


@attr.s
class Source:
    make = classmethod(make)

    title = attr.ib()
    source = attr.ib()

    iconUrl = attr.ib()
    isBrowsable = attr.ib()
    isPlayable = attr.ib()
    meta = attr.ib()
    playAction = attr.ib()

    def __str__(self):
        return "%s (%s)" % (self.title, self.source)


@attr.s
class Volume:
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
        return self.mute == 'on'

    def __str__(self):
        s = "Volume: %s/%s" % (self.volume, self.maxVolume)
        if self.is_muted:
            s += " (muted)"
        return s

    async def set_mute(self, activate):
        enabled = "off"
        if activate:
            enabled = "on"

        return await self.services["audio"]["setAudioMute"](mute=enabled, output=self.output)

    async def toggle_mute(self):
        return await self.services["audio"]["setAudioMute"](mute="toggle", output=self.output)

    async def set_volume(self, volume):
        return await self.services["audio"]["setAudioVolume"](volume=str(volume), output=self.output)


@attr.s
class VolumeChange(ChangeNotification):
    make = classmethod(make)

    mute = attr.ib(convert=lambda x: True if x == "on" else False)
    volume = attr.ib()


@attr.s
class Power:
    make = classmethod(make)

    status = attr.ib(convert=lambda x: True if x == "active" else False)
    standbyDetail = attr.ib()

    def __bool__(self):
        return self.status

    def __str__(self):
        if self.status:
            return "Power on"
        else:
            return "Power off"


@attr.s
class PowerChange(ChangeNotification, Power):
    pass


@attr.s
class Input:
    make = classmethod(make)

    meta = attr.ib()
    connection = attr.ib()
    title = attr.ib()
    uri = attr.ib()

    services = attr.ib(repr=False)
    active = attr.ib(convert=lambda x: True if x == 'active' else False)
    label = attr.ib()
    iconUrl = attr.ib()
    outputs = attr.ib()

    def __str__(self):
        s = "%s (uri: %s)" % (self.title, self.uri)
        if self.active:
            s += " (active)"
        return s

    async def activate(self):
        """Activate this input."""
        return await self.services["avContent"]["setPlayContent"](uri=self.uri)


@attr.s
class Storage:
    make = classmethod(make)

    deviceName = attr.ib()
    uri = attr.ib()
    volumeLabel = attr.ib()

    freeCapacityMB = attr.ib()
    systemAreaCapacityMB = attr.ib()
    wholeCapacityMB = attr.ib()

    formattable = attr.ib()
    formatting = attr.ib()

    isAvailable = attr.ib(convert=convert_bool)
    mounted = attr.ib(convert=lambda x: True if x == 'mounted' else False)
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
            self.mounted
        )


@attr.s
class ApiMapping:
    make = classmethod(make)

    service = attr.ib()
    getApi = attr.ib()

    setApi = attr.ib()
    target = attr.ib()
    targetSuppl = attr.ib()


@attr.s
class SettingsEntry:
    make = classmethod(make)

    isAvailable = attr.ib()
    type = attr.ib()

    def convert_if_available(x):
        if x is not None:
            return [SettingsEntry.make(**y) for y in x]

    def convert_if_available_mapping(x):
        if x is not None:
            return ApiMapping.make(**x)

    async def get_value(self, dev):
        """Returns current value for this setting."""
        res = await dev.get_setting(self.apiMapping.service,
                                    self.apiMapping.getApi['name'],
                                    self.apiMapping.target)
        return Setting.make(**res.pop())

    @property
    def is_directory(self):
        return self.type == 'directory'

    apiMapping = attr.ib(convert=convert_if_available_mapping, repr=False)
    settings = attr.ib(convert=convert_if_available)
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
    Use candidate to access the potential values"""
    make = classmethod(make)

    def create_candidates(x):
        if x is not None:
            return [SettingCandidate.make(**y) for y in x]

        return []

    currentValue = attr.ib()
    target = attr.ib()
    type = attr.ib()
    candidate = attr.ib(convert=create_candidates)  # type: List[SettingCandidate]
    isAvailable = attr.ib()
    title = attr.ib()
    titleTextID = attr.ib()
    deviceUIInfo = attr.ib()
    uri = attr.ib()


@attr.s
class SettingChange(ChangeNotification):
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
        self.currentValue = self.apiMappingUpdate["currentValue"]
        self.target = self.apiMappingUpdate["target"]

    def __str__(self):
        return "<SettingChange %s (%s): %s>" % (self.title,
                                                self.target,
                                                self.currentValue)

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
        return self.contentKind == 'input'


@attr.s
class NotificationChange(ChangeNotification):
    """Container for storing information about state of Notifications."""
    make = classmethod(make)

    enabled = attr.ib(convert=lambda x: [x["name"] for x in x])
    disabled = attr.ib(convert=lambda x: [x["name"] for x in x])

    def __str__(self):
        return "<NotificationChange enabled: %s disabled: %s>" % (
            ",".join(self.enabled),
            ",".join(self.disabled)
        )
