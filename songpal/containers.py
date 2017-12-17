from datetime import timedelta
from typing import List
import attr


@attr.s
class Scheme:
    scheme = attr.ib()


@attr.s
class PlaybackFunction:
    function = attr.ib()


@attr.s
class SupportedFunctions:
    uri = attr.ib()
    functions = attr.ib(convert=lambda x: [PlaybackFunction(y) for y in x])


@attr.s
class ContentInfo:
    capability = attr.ib()
    count = attr.ib()


@attr.s
class Content:
    isBrowsable = attr.ib()
    uri = attr.ib()
    contentKind = attr.ib()

    isPlayable = attr.ib()
    index = attr.ib()
    title = attr.ib(default=None)  # no idea why this would be missing..
    folderNo = attr.ib(default=None)  # files do not have this
    fileNo = attr.ib(default=None)  # folders do not have this
    parentUri = attr.ib(default=None)  # toplevel has no parents

    fileSizeByte = attr.ib(default=None)  # dirs do not have this
    createdTime = attr.ib(default=None)

    def __str__(self):
        return "%s (%s, kind: %s)" % (self.title, self.uri, self.contentKind)


@attr.s
class StateInfo:
    state = attr.ib()
    supplement = attr.ib()


@attr.s
class PlayInfo:
    """This is only tested on music files,
    the outs for the method call is much, much larger"""
    stateInfo = attr.ib(convert=lambda x: StateInfo(**x))
    contentKind = attr.ib()
    uri = attr.ib()
    output = attr.ib()

    # only available when being played
    artist = attr.ib(default=None)
    albumName = attr.ib(default=None)
    title = attr.ib(default=None)
    durationMsec = attr.ib(default=None)
    mediaType = attr.ib(default=None)
    parentUri = attr.ib(default=None)
    positionMsec = attr.ib(default=None)
    repeatType = attr.ib(default=None)
    source = attr.ib(default=None)

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
    productName = attr.ib()
    modelName = attr.ib()
    productCategory = attr.ib()
    interfaceVersion = attr.ib()
    serverName = attr.ib()


@attr.s
class Sysinfo:
    bdAddr = attr.ib()
    macAddr = attr.ib()
    version = attr.ib()
    wirelessMacAddr = attr.ib()


@attr.s
class UpdateInfo:
    isUpdatable = attr.ib()


@attr.s
class Source:
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
    services = attr.ib(repr=False)
    maxVolume = attr.ib()
    minVolume = attr.ib()
    mute = attr.ib()
    output = attr.ib()
    step = attr.ib()
    volume = attr.ib()

    @property
    def muted(self):
        return self.mute == 'on'

    def __str__(self):
        s = "Volume: %s/%s" % (self.volume, self.maxVolume)
        if self.muted:
            s += " (muted)"
        return s

    async def set_mute(self, activate):
        enabled = "off"
        if activate:
            enabled = "on"

        return await self.services["audio"]["setAudioMute"](mute=enabled)

    async def set_volume(self, volume):
        return await self.services["audio"]["setAudioVolume"](volume=str(volume))


@attr.s
class Power:
    status = attr.ib(convert=lambda x: True if x == "active" else False)
    standbyDetail = attr.ib(default=None)

    def __bool__(self):
        return self.status

    def __str__(self):
        if self.status:
            return "Power on"
        else:
            return "Power off"


@attr.s
class Output:
    services = attr.ib(repr=False)
    title = attr.ib()
    uri = attr.ib()
    active = attr.ib(convert=lambda x: True if x == 'active' else False)
    meta = attr.ib()
    label = attr.ib()
    iconUrl = attr.ib()
    connection = attr.ib()

    def __str__(self):
        s = "%s (uri: %s)" % (self.title, self.uri)
        if self.active:
            s += " (active)"
        return s

    async def activate(self):
        """Activate this output."""
        return await self.services["avContent"]["setPlayContent"](uri=self.uri)


@attr.s
class Storage:
    deviceName = attr.ib()
    uri = attr.ib()
    volumeLabel = attr.ib()

    freeCapacityMB = attr.ib()
    systemAreaCapacityMB = attr.ib()
    wholeCapacityMB = attr.ib()

    formattable = attr.ib()
    formatting = attr.ib()

    isAvailable = attr.ib(convert=lambda x: True if x == 'true' else False)
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
    service = attr.ib()
    getApi = attr.ib()

    setApi = attr.ib(default=None)
    target = attr.ib(default=None)
    targetSuppl = attr.ib(default=None)


@attr.s
class SettingsEntry:
    isAvailable = attr.ib()
    type = attr.ib()

    def convert_if_available(x):
        if x is not None:
            return [SettingsEntry(**y) for y in x]

    def convert_if_available_mapping(x):
        if x is not None:
            return ApiMapping(**x)

    async def get_value(self, dev):
        """Returns current value for this setting."""
        res = await dev.get_setting(self.apiMapping.service,
                                    self.apiMapping.getApi['name'],
                                    self.apiMapping.target)
        return Setting(**res.pop())

    @property
    def is_directory(self):
        return self.type == 'directory'

    apiMapping = attr.ib(convert=convert_if_available_mapping, default=None, repr=False)
    settings = attr.ib(convert=convert_if_available, default=None)
    title = attr.ib(default=None)
    titleTextID = attr.ib(default=None)
    usage = attr.ib(None)
    deviceUIInfo = attr.ib(None)

    def __str__(self):
        return "%s (%s, %s)" % (self.title, self.titleTextID, self.type)


@attr.s
class SettingCandidate:
    """Representation of a setting candidate aka. option."""
    title = attr.ib()
    value = attr.ib()
    isAvailable = attr.ib()
    min = attr.ib(default=None)
    max = attr.ib(default=None)
    step = attr.ib(default=None)
    titleTextID = attr.ib(default=None)


@attr.s
class Setting:
    """Representation of a setting.
    Use candidate to access the potential values"""
    currentValue = attr.ib()
    target = attr.ib()
    type = attr.ib()
    candidate = attr.ib(convert=lambda x: [SettingCandidate(**y) for y in x], default=[])  # type: List[SettingCandidate]
    isAvailable = attr.ib(default=None)
    title = attr.ib(default=None)
    titleTextID = attr.ib(default=None)
    deviceUIInfo = attr.ib(default=None)
    uri = attr.ib(default=None)
