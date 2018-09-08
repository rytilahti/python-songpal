import asyncio
import itertools
import json
import logging
from pprint import pprint as pp, pformat as pf
from typing import List, Dict
from urllib.parse import urlparse
from collections import defaultdict

import requests

from songpal.containers import (
    Power, PlayInfo, Setting, SettingsEntry, InterfaceInfo, Sysinfo,
    Storage, SupportedFunctions, Input, Source, SoftwareUpdateInfo,
    ContentInfo, Volume, Scheme, Content)
from songpal.service import Service
from songpal.notification import Notification
from songpal.common import SongpalException

_LOGGER = logging.getLogger(__name__)


class Device:
    WEBSOCKET_PROTOCOL = "v10.webapi.scalar.sony.com"
    WEBSOCKET_VERSION = 13

    def __init__(self, endpoint, force_protocol=None, debug=0):
        self.debug = debug
        endpoint = urlparse(endpoint)
        self.endpoint = endpoint.geturl()
        _LOGGER.debug("Endpoint: %s" % self.endpoint)

        self.guide_endpoint = endpoint._replace(path='/sony/guide').geturl()
        _LOGGER.debug("Guide endpoint: %s" % self.guide_endpoint)

        if force_protocol:
            _LOGGER.warning("Forcing protocol %s", force_protocol)
        self.force_protocol = force_protocol

        self.idgen = itertools.count(start=1)
        self.services = {}  # type: Dict[str, Service]

        self.callbacks = defaultdict(set)

    async def __aenter__(self):
        await self.get_supported_methods()

    async def create_post_request(self, method, params):
        headers = {"Content-Type": "application/json"}
        payload = {"method": method,
                   "params": [params],
                   "id": next(self.idgen),
                   "version": "1.0"}
        req = requests.Request("POST", self.guide_endpoint,
                               data=json.dumps(payload), headers=headers)
        prepreq = req.prepare()
        s = requests.Session()
        try:
            response = s.send(prepreq)
            if response.status_code != 200:
                _LOGGER.error("Got !200 response: %s" % response.text)
                return None

            response = response.json()
        except requests.RequestException as ex:
            raise SongpalException("Unable to get APIs: %s" % ex) from ex

        if self.debug > 1:
            _LOGGER.debug("Got getSupportedApiInfo: %s", pf(response))

        return response

    async def request_supported_methods(self):
        """Return JSON formatted supported API."""
        return await self.create_post_request("getSupportedApiInfo", {})

    async def get_supported_methods(self):
        """Get information about supported methods.
        Calling this as the first thing before doing anything else is
        necessary to fill the available services table.
        """
        response = await self.request_supported_methods()

        if "result" in response:
            services = response["result"][0]
            _LOGGER.debug("Got %s services!" % len(services))

            for x in services:
                serv = await Service.from_payload(x,
                                                  self.endpoint,
                                                  self.idgen,
                                                  self.debug,
                                                  self.force_protocol)
                if serv is not None:
                    self.services[x["service"]] = serv
                else:
                    _LOGGER.warning("Unable to create service %s", x["service"])

            for service in self.services.values():
                if self.debug > 1:
                    _LOGGER.debug("Service %s", service)
                for api in service.methods:
                    # self.logger.debug("%s > %s" % (service, api))
                    if self.debug > 1:
                        _LOGGER.debug("> %s" % api)
            return self.services

        return None

    async def get_power(self) -> Power:
        """Get the device state"""
        res = await self.services["system"]["getPowerStatus"]()
        return Power.make(**res)

    async def set_power(self, value: bool):
        """Toggle the device on and off."""
        if value:
            status = "active"
        else:
            status = "off"
        # TODO WoL works when quickboot is not enabled
        return await self.services["system"]["setPowerStatus"](status=status)

    async def get_play_info(self) -> PlayInfo:
        """Return  of the device."""
        info = await self.services["avContent"]["getPlayingContentInfo"]({})
        return PlayInfo.make(**info.pop())

    async def get_power_settings(self) -> List[Setting]:
        """Get power settings."""
        return [Setting(**x)
                for x in await self.services["system"]["getPowerSettings"]({})]

    async def set_power_settings(self, target: str, value: str) -> None:
        """Set power settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["system"]["setPowerSettings"](params)

    async def get_wutang(self) -> List[Setting]:
        """Get Googlecast settings."""
        return [Setting(**x)
                for x in await self.services["system"]["getWuTangInfo"]({})]

    async def set_wutang(self, target: str, value: str):
        """Set Googlecast settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["system"]["setWuTangSettings"](params)

    async def request_settings(self):
        settings = await self.services["system"]["getSettingsTree"](usage="")
        return settings

    async def get_settings(self) -> List[SettingsEntry]:
        settings = await self.request_settings()
        return [SettingsEntry.make(**x) for x in settings["settings"]]

    async def get_misc_settings(self) -> List[Setting]:
        """Return miscellaneous settings such as name and timezone."""
        misc = await self.services["system"]["getDeviceMiscSettings"](target="")
        return [Setting.make(**x) for x in misc]

    async def set_misc_settings(self, target: str, value: str):
        """Change miscellaneous settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["system"]["setDeviceMiscSettings"](params)

    async def get_interface_information(self) -> InterfaceInfo:
        """Return generic product information."""
        iface = await self.services["system"]["getInterfaceInformation"]()
        return InterfaceInfo.make(**iface)

    async def get_system_info(self) -> Sysinfo:
        """Return system information including mac addresses and current version."""
        return Sysinfo.make(**await self.services["system"]["getSystemInformation"]())

    async def get_sleep_timer_settings(self) -> List[Setting]:
        """Get sleep timer settings."""
        return [Setting.make(**x) for x
                in await self.services["system"]["getSleepTimerSettings"]({})]

    async def get_storage_list(self) -> List[Storage]:
        """Return information about connected storage devices."""
        return [Storage.make(**x) for x
                in await self.services["system"]["getStorageList"]({})]

    async def get_update_info(self, from_network=True) -> SoftwareUpdateInfo:
        """Get information about updates."""
        if from_network:
            from_network = "true"
        else:
            from_network = "false"
        #from_network = ""
        info = await self.services["system"]["getSWUpdateInfo"](network=from_network)
        return SoftwareUpdateInfo.make(**info)

    async def activate_system_update(self) -> None:
        return await self.services["system"]["actSWUpdate"]()

    async def get_inputs(self) -> List[Input]:
        """Return list of available outputs."""
        res = await self.services["avContent"]["getCurrentExternalTerminalsStatus"]()
        return [Input.make(services=self.services, **x) for x in res]

    async def get_setting(self, service: str, method: str, target: str):
        return await self.services[service][method](target=target)

    async def get_bluetooth_settings(self) -> List[Setting]:
        """Get bluetooth settings."""
        bt = await self.services["avContent"]["getBluetoothSettings"]({})
        return [Setting(**x) for x in bt]

    async def set_bluetooth_settings(self, target: str, value: str) -> None:
        """Set bluetooth settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["avContent"]["setBluetoothSettings"](params)

    async def get_custom_eq(self):
        """Get custom EQ settings."""
        return await self.services["audio"]["getCustomEqualizerSettings"]({})

    async def set_custom_eq(self, target: str, value: str) -> None:
        """Set custom EQ settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["audio"]["setCustomEqualizerSettings"](params)

    async def get_supported_playback_functions(self, uri='') -> List[SupportedFunctions]:
        """Return list of inputs and their supported functions."""
        return [SupportedFunctions.make(**x) for x in
                await self.services["avContent"]["getSupportedPlaybackFunction"](uri=uri)]

    async def get_playback_settings(self) -> List[Setting]:
        """Get playback settings such as shuffle and repeat."""
        return [Setting.make(**x) for x
                in await self.services["avContent"]["getPlaybackModeSettings"]({})]

    async def set_playback_settings(self, target, value) -> None:
        """Set playback settings such a shuffle and repeat."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["avContent"]["setPlaybackModeSettings"](params)

    async def get_schemes(self) -> List[Scheme]:
        """Return supported uri schemes."""
        return [Scheme.make(**x) for x
                in await self.services["avContent"]["getSchemeList"]()]

    async def get_source_list(self, scheme: str = '') -> List[Source]:
        """Return available sources for playback?"""
        res = await self.services["avContent"]["getSourceList"](scheme=scheme)
        return [Source.make(**x) for x in res]

    async def get_content_count(self, source: str):
        """Return file listing for source."""
        params = {
            'uri': source,
            'type': None,
            'target': 'all',
            'view': 'flat'
        }
        return ContentInfo.make(
            **await self.services["avContent"]["getContentCount"](params))

    async def get_contents(self, uri, depth=0):
        contents = [Content.make(**x) for x
                    in await self.services["avContent"]["getContentList"](uri=uri)]
        contentlist = []

        for content in contents:
            if content.contentKind == 'directory' and content.index >= 0:
                # print("got directory %s" % content.uri)
                res = await self.get_contents(content.uri, depth + 4)
                contentlist.extend(res)
            else:
                contentlist.append(content)
                # print("%s%s" % (' ' * depth, content))
        return contentlist

    async def get_volume_information(self) -> List[Volume]:
        """Get the volume information."""
        res = await self.services["audio"]["getVolumeInformation"]({})
        volume_info = [Volume.make(services=self.services, **x) for x in res]
        if len(volume_info) < 1:
            logging.warning("Unable to get volume information")
        elif len(volume_info) > 1:
            logging.debug("The device seems to have more than one volume setting.")
        return volume_info

    async def get_sound_settings(self, target='') -> List[Setting]:
        """Get the current sound settings.

        :param str target: settings target, defaults to all.
        """
        res = await self.services["audio"]["getSoundSettings"]({"target": target})
        return [Setting.make(**x) for x in res]

    async def get_soundfield(self) -> List[Setting]:
        """Get the current sound field settings."""
        res = await self.services["audio"]["getSoundSettings"]({"target": "soundField"})
        return Setting.make(**res[0])

    async def set_soundfield(self, value):
        """Set soundfield."""
        return await self.set_sound_settings('soundField', value)

    async def set_sound_settings(self, target: str, value: str):
        """Change a sound setting."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["audio"]["setSoundSettings"](params)

    async def get_speaker_settings(self) -> List[Setting]:
        """Return speaker settings."""
        speaker_settings = await self.services["audio"]["getSpeakerSettings"]({})
        return [Setting.make(**x) for x in speaker_settings]

    async def set_speaker_settings(self, target: str, value: str):
        """Set speaker settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["audio"]["setSpeakerSettings"](params)

    async def get_available_playback_functions(self, output=""):
        """Return available playback functions,
        if no output is given the current is assumed."""
        await self.services["avContent"]["getAvailablePlaybackFunction"](output=output)

    def on_notification(self, type_, callback):
        self.callbacks[type_].add(callback)

    async def listen_notifications(self):
        tasks = []
        async def handle_notification(notification):
            if type(notification) not in self.callbacks:
                _LOGGER.debug("No callbacks for %s", notification)
                return
            for cb in self.callbacks[type(notification)]:
                await cb(notification)

        for serv in self.services.values():
            tasks.append(asyncio.ensure_future(
                serv.listen_all_notifications(handle_notification)))

        await asyncio.wait(tasks)

    async def get_notifications(self) -> List[Notification]:
        notifications = []
        for serv in self.services:
            for notification in self.services[serv].notifications:
                notifications.append(notification)
        return notifications

    async def raw_command(self, service, method, params):
        _LOGGER.info("Calling %s.%s(%s)", service, method, params)
        return await self.services[service][method](params)
