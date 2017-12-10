"""
Support for Songpal-enabled (Sony) media devices.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/media_player.songpal/
"""
import logging
import asyncio

import voluptuous as vol

from homeassistant.components.media_player import (
    PLATFORM_SCHEMA, SUPPORT_SELECT_SOURCE, SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET,
    MediaPlayerDevice)
from homeassistant.const import (
    CONF_NAME, STATE_UNKNOWN, STATE_ON, STATE_OFF)
import homeassistant.helpers.config_validation as cv

SUPPORT_SONGPAL = SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE

_LOGGER = logging.getLogger(__name__)

# to ignore: Failing the WebSocket connection: 1006
logging.getLogger("websockets.protocol").setLevel(logging.WARNING)

CONF_ENDPOINT = "endpoint"
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=None): cv.string,
    vol.Required(CONF_ENDPOINT): cv.string,
})


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the Songpal platform."""
    devices = []
    if discovery_info:
        _LOGGER.error("got autodiscovered device: %s" % discovery_info)
        devices.append(SongpalDevice(discovery_info["name"],
                       discovery_info["properties"]["endpoint"]))
    else:
        songpal = SongpalDevice(config.get(CONF_NAME),
                                config.get(CONF_ENDPOINT))
        devices.append(songpal)

    async_add_devices(devices, True)


class SongpalDevice(MediaPlayerDevice):
    def __init__(self, name, endpoint):
        import songpal
        self._name = name
        self.endpoint = endpoint
        self._dev = songpal.Protocol(self.endpoint)
        self._is_initialized = False
        self._state = False
        self._volume_min = 0
        self._volume_max = 1
        self._volume = 0
        self._is_muted = False
        self._outputs = []
        self._available = False

    @property
    def name(self):
        return self._name

    @property
    def available(self):
        return self._available

    @asyncio.coroutine
    def async_added_to_hass(self):
        yield from self._dev.get_supported_methods()

    @property
    def dev(self):
        return self._dev

    @asyncio.coroutine
    def async_update(self):
        try:
            volumes = yield from self.dev.get_volume_information()
            if len(volumes) != 1:
                _LOGGER.error("Unknown amount of volumes, bailing out: %s" % volumes)
                return

            vol = volumes.pop()
            _LOGGER.debug("Got volume info: %s vol", vol)
            self._volume_max = vol.maxVolume
            self._volume_min = vol.minVolume
            self._volume = vol.volume
            self._volume_control = vol
            self._is_muted = self._volume_control.mute == 'on'

            status = yield from self.dev.get_power()
            self._state = status.status
            _LOGGER.debug("Got state: %s" % status)

            outs = yield from self.dev.get_outputs()
            _LOGGER.debug("Got outs: %s" % outs)
            self._outputs = outs

            self._available = True
        except Exception as ex:
            self._available = False

    @asyncio.coroutine
    def async_select_source(self, source):
        for out in self._outputs:
            if out.title == source:
                yield from out.activate()
                return

        _LOGGER.error("Unable to find output: %s" % source)

    @property
    def source_list(self):
        return [x.title for x in self._outputs]

    @property
    def state(self):
        if self._state:
            return STATE_ON
        else:
            return STATE_OFF

    @property
    def source(self):
        for out in self._outputs:
            if out.active:
                return out.title

        _LOGGER.error("Unable to find active output!")

    @property
    def volume_level(self):
        """We gotta return volume [0,1]"""
        volume = self._volume / self._volume_max
        _LOGGER.debug("current volume: %s" % volume)
        return volume

    @asyncio.coroutine
    def async_set_volume_level(self, volume):
        """We receive volume [0,1]"""
        vol = int(volume * self._volume_max)
        _LOGGER.info("Setting volume to %s" % vol)
        return self._volume_control.set_volume(vol)

    @asyncio.coroutine
    def async_turn_on(self):
        return self.dev.set_power(True)

    @asyncio.coroutine
    def async_turn_off(self):
        return self.dev.set_power(False)

    @asyncio.coroutine
    def async_mute_volume(self, mute):
        _LOGGER.info("set mute: %s" % mute)
        return self._volume_control.set_mute(mute)

    @property
    def is_volume_muted(self):
        return self._is_muted

    @property
    def supported_features(self):
        return SUPPORT_SONGPAL
