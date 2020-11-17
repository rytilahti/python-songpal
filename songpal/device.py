"""Module presenting a single supported device."""
import asyncio
import itertools
import logging
from collections import defaultdict
from pprint import pformat as pf
from typing import Any, Dict, List, Mapping
from urllib.parse import urlparse

import aiohttp
from async_upnp_client import UpnpFactory
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.profiles.dlna import DmrDevice
from async_upnp_client.search import async_search

from didl_lite import didl_lite
from songpal.common import ProtocolType, SongpalException
from songpal.containers import (
    Content,
    ContentInfo,
    Input,
    InputControlSongpal,
    InputControlUpnp,
    InterfaceInfo,
    PlayInfo,
    Power,
    Scheme,
    Setting,
    SettingsEntry,
    SoftwareUpdateInfo,
    Source,
    Storage,
    SupportedFunctions,
    Sysinfo,
    Volume,
    VolumeControlSongpal,
    VolumeControlUpnp,
    Zone,
)
from songpal.discovery import Discover
from songpal.notification import ConnectChange, Notification
from songpal.service import Service

_LOGGER = logging.getLogger(__name__)


class Device:
    """This is the main entry point for communicating with a device.

    In order to use this you need to obtain the URL for the API first.
    """

    WEBSOCKET_PROTOCOL = "v10.webapi.scalar.sony.com"
    WEBSOCKET_VERSION = 13

    def __init__(self, endpoint, force_protocol=None, debug=0):
        """Initialize Device.

        :param endpoint: the main API endpoint.
        :param force_protocol: can be used to force the protocol (xhrpost/websocket).
        :param debug: debug level. larger than 1 gives even more debug output.
        """
        self.debug = debug
        endpoint = urlparse(endpoint)
        self.endpoint = endpoint.geturl()
        _LOGGER.debug("Endpoint: %s" % self.endpoint)

        self.guide_endpoint = endpoint._replace(path="/sony/guide").geturl()
        _LOGGER.debug("Guide endpoint: %s" % self.guide_endpoint)

        if force_protocol:
            _LOGGER.warning("Forcing protocol %s", force_protocol)
        self.force_protocol = force_protocol

        self.idgen = itertools.count(start=1)
        self.services = {}  # type: Dict[str, Service]

        self.callbacks = defaultdict(set)

    async def __aenter__(self):
        """Asynchronous context manager, initializes the list of available methods."""
        await self.get_supported_methods()

    async def create_post_request(self, method: str, params: Dict = None):
        """Call the given method over POST.

        :param method: Name of the method
        :param params: dict of parameters
        :return: JSON object
        """
        if params is None:
            params = {}
        headers = {"Content-Type": "application/json"}
        payload = {
            "method": method,
            "params": [params],
            "id": next(self.idgen),
            "version": "1.0",
        }

        if self.debug > 1:
            _LOGGER.debug("> POST %s with body: %s", self.guide_endpoint, payload)

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                res = await session.post(
                    self.guide_endpoint, json=payload, headers=headers
                )
                if self.debug > 1:
                    _LOGGER.debug("Received %s: %s" % (res.status, res.text))
                if res.status != 200:
                    res_json = await res.json(content_type=None)
                    raise SongpalException(
                        "Got a non-ok (status %s) response for %s"
                        % (res.status, method),
                        error=res_json.get("error"),
                    )

                res_json = await res.json(content_type=None)
        except (aiohttp.InvalidURL, aiohttp.ClientConnectionError) as ex:
            raise SongpalException("Unable to do POST request: %s" % ex) from ex

        if "error" in res_json:
            raise SongpalException(
                "Got an error for %s" % method, error=res_json["error"]
            )

        if self.debug > 1:
            _LOGGER.debug("Got %s: %s", method, pf(res_json))

        return res_json

    async def request_supported_methods(self):
        """Return JSON formatted supported API."""
        return await self.create_post_request("getSupportedApiInfo")

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
                serv = await Service.from_payload(
                    x, self.endpoint, self.idgen, self.debug, self.force_protocol
                )
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
        """Get the device state."""
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
        return [
            Setting.make(**x)
            for x in await self.services["system"]["getPowerSettings"]({})
        ]

    async def set_power_settings(self, target: str, value: str) -> None:
        """Set power settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["system"]["setPowerSettings"](params)

    async def get_googlecast_settings(self) -> List[Setting]:
        """Get Googlecast settings."""
        return [
            Setting.make(**x)
            for x in await self.services["system"]["getWuTangInfo"]({})
        ]

    async def set_googlecast_settings(self, target: str, value: str):
        """Set Googlecast settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["system"]["setWuTangInfo"](params)

    async def request_settings_tree(self):
        """Get raw settings tree JSON.

        Prefer :func:get_settings: for containerized settings.
        """
        settings = await self.services["system"]["getSettingsTree"](usage="")
        return settings

    async def get_settings(self) -> List[SettingsEntry]:
        """Get a list of available settings.

        See :func:request_settings_tree: for raw settings.
        """
        settings = await self.request_settings_tree()
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
        return [
            Setting.make(**x)
            for x in await self.services["system"]["getSleepTimerSettings"]({})
        ]

    async def get_storage_list(self) -> List[Storage]:
        """Return information about connected storage devices."""
        return [
            Storage.make(**x)
            for x in await self.services["system"]["getStorageList"]({})
        ]

    async def get_update_info(self, from_network=True) -> SoftwareUpdateInfo:
        """Get information about updates."""
        if from_network:
            from_network = "true"
        else:
            from_network = "false"
        # from_network = ""
        info = await self.services["system"]["getSWUpdateInfo"](network=from_network)
        return SoftwareUpdateInfo.make(**info)

    async def activate_system_update(self) -> None:
        """Start a system update if available."""
        return await self.services["system"]["actSWUpdate"]()

    async def get_inputs(self) -> List[Input]:
        """Return list of available outputs."""
        res = await self.services["avContent"]["getCurrentExternalTerminalsStatus"]()
        return [
            InputControlSongpal.make(services=self.services, **x)
            for x in res
            if "meta:zone:output" not in x["meta"]
        ]

    async def get_zones(self) -> List[Zone]:
        """Return list of available zones."""
        res = await self.services["avContent"]["getCurrentExternalTerminalsStatus"]()
        zones = [
            Zone.make(services=self.services, **x)
            for x in res
            if "meta:zone:output" in x["meta"]
        ]
        if not zones:
            raise SongpalException("Device has no zones")
        return zones

    async def get_zone(self, name) -> Zone:
        zones = await self.get_zones()
        try:
            zone = next((x for x in zones if x.title == name))
            return zone
        except StopIteration:
            raise SongpalException("Unable to find zone %s" % name)

    async def get_setting(self, service: str, method: str, target: str):
        """Get a single setting for service.

        :param service: Service to query.
        :param method: Getter method for the setting, read from ApiMapping.
        :param target: Setting to query.
        :return: JSON response from the device.
        """
        return await self.services[service][method](target=target)

    async def get_bluetooth_settings(self) -> List[Setting]:
        """Get bluetooth settings."""
        bt = await self.services["avContent"]["getBluetoothSettings"]({})
        return [Setting.make(**x) for x in bt]

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

    async def get_supported_playback_functions(
        self, uri=""
    ) -> List[SupportedFunctions]:
        """Return list of inputs and their supported functions."""
        return [
            SupportedFunctions.make(**x)
            for x in await self.services["avContent"]["getSupportedPlaybackFunction"](
                uri=uri
            )
        ]

    async def get_playback_settings(self) -> List[Setting]:
        """Get playback settings such as shuffle and repeat."""
        return [
            Setting.make(**x)
            for x in await self.services["avContent"]["getPlaybackModeSettings"]({})
        ]

    async def set_playback_settings(self, target, value) -> None:
        """Set playback settings such a shuffle and repeat."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self.services["avContent"]["setPlaybackModeSettings"](params)

    async def get_schemes(self) -> List[Scheme]:
        """Return supported uri schemes."""
        return [
            Scheme.make(**x)
            for x in await self.services["avContent"]["getSchemeList"]()
        ]

    async def get_source_list(self, scheme: str = "") -> List[Source]:
        """Return available sources for playback."""
        res = await self.services["avContent"]["getSourceList"](scheme=scheme)
        return [Source.make(**x) for x in res]

    async def get_content_count(self, source: str):
        """Return file listing for source."""
        params = {"uri": source, "type": None, "target": "all", "view": "flat"}
        return ContentInfo.make(
            **await self.services["avContent"]["getContentCount"](params)
        )

    async def get_contents(self, uri) -> List[Content]:
        """Request content listing recursively for the given URI.

        :param uri: URI for the source.
        :return: List of Content objects.
        """
        contents = [
            Content.make(**x)
            for x in await self.services["avContent"]["getContentList"](uri=uri)
        ]
        contentlist = []

        for content in contents:
            if content.contentKind == "directory" and content.index >= 0:
                # print("got directory %s" % content.uri)
                res = await self.get_contents(content.uri)
                contentlist.extend(res)
            else:
                contentlist.append(content)
                # print("%s%s" % (' ' * depth, content))
        return contentlist

    async def get_volume_information(self) -> List[Volume]:
        """Get the volume information."""
        res = await self.services["audio"]["getVolumeInformation"]({})
        volume_info = [
            VolumeControlSongpal.make(services=self.services, **x) for x in res
        ]
        if len(volume_info) < 1:
            logging.warning("Unable to get volume information")
        elif len(volume_info) > 1:
            logging.debug("The device seems to have more than one volume setting.")
        return volume_info

    async def get_sound_settings(self, target="") -> List[Setting]:
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
        return await self.set_sound_settings("soundField", value)

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
        """Return available playback functions.

        If no output is given the current is assumed.
        """
        await self.services["avContent"]["getAvailablePlaybackFunction"](output=output)

    def on_notification(self, type_, callback):
        """Register a notification callback.

        The callbacks registered by this method are called when an expected
        notification is received from the device.
        To listen for notifications call :func:listen_notifications:.
        :param type_: Type of the change, e.g., VolumeChange or PowerChange
        :param callback: Callback to call when a notification is received.
        :return:
        """
        self.callbacks[type_].add(callback)

    def clear_notification_callbacks(self):
        """Clear all notification callbacks."""
        self.callbacks.clear()

    async def listen_notifications(self, fallback_callback=None):
        """Listen for notifications from the device forever.

        Use :func:on_notification: to register what notifications to listen to.
        """
        tasks = []

        async def handle_notification(notification):
            if type(notification) not in self.callbacks:
                if not fallback_callback:
                    _LOGGER.debug("No callbacks for %s", notification)
                    # _LOGGER.debug("Existing callbacks for: %s" % self.callbacks)
                else:
                    await fallback_callback(notification)
                return
            for cb in self.callbacks[type(notification)]:
                await cb(notification)

        for serv in self.services.values():
            tasks.append(
                asyncio.ensure_future(
                    serv.listen_all_notifications(handle_notification)
                )
            )

        try:
            print(await asyncio.gather(*tasks))
        except Exception as ex:
            # TODO: do a slightly restricted exception handling?
            # Notify about disconnect
            await handle_notification(ConnectChange(connected=False, exception=ex))
            return

    async def stop_listen_notifications(self):
        """Stop listening on notifications."""
        _LOGGER.debug("Stopping listening for notifications..")
        for serv in self.services.values():
            await serv.stop_listen_notifications()

        return True

    async def get_notifications(self) -> List[Notification]:
        """Get available notifications, which can then be subscribed to.

        Call :func:activate: to enable notifications, and :func:listen_notifications:
        to loop forever for notifications.

        :return: List of Notification objects
        """
        notifications = []
        for serv in self.services:
            for notification in self.services[serv].notifications:
                notifications.append(notification)
        return notifications

    async def raw_command(self, service: str, method: str, params: Any):
        """Call an arbitrary method with given parameters.

        This is useful for debugging and trying out commands before
        implementing them properly.
        :param service: Service, use list(self.services) to get a list of availables.
        :param method: Method to call.
        :param params: Parameters as a python object (e.g., dict, list)
        :return: Raw JSON response from the device.
        """
        _LOGGER.info("Calling %s.%s(%s)", service, method, params)
        return await self.services[service][method](params)


class UpnpDevice(Device):
    def __init__(self, endpoint, force_protocol=None, debug=0):
        super().__init__(endpoint, force_protocol=force_protocol, debug=debug)
        self._upnp_discovery = None
        self._upnp_server = None
        self._upnp_renderer = None

    @staticmethod
    async def create(endpoint, force_protocol=None, debug=0, timeout=5):
        self = UpnpDevice(endpoint, force_protocol=force_protocol, debug=debug)
        await self.discover(timeout=timeout)
        return self

    async def discover(self, timeout=5):
        host = urlparse(self.endpoint).hostname

        sony_device_future = asyncio.Future()
        media_renderer_future = asyncio.Future()

        requester = AiohttpRequester()
        factory = UpnpFactory(requester)

        search_cancel_event = asyncio.Event()

        async def on_response(data: Mapping[str, str]) -> None:
            print(data)
            if "st" not in data or "location" not in data:
                return

            if urlparse(data["location"]).hostname != host:
                return

            if data["st"] == Discover.ST:
                device = await Discover.parse_device(data)
                if device:
                    sony_device_future.set_result(device)

            if data["st"] in DmrDevice.DEVICE_TYPES:
                media_renderer_future.set_result(data["location"])

            if sony_device_future.done() and media_renderer_future.done():
                search_cancel_event.set()

        search_finished_future = async_search(
            async_callback=on_response, timeout=timeout
        )
        data_found_future = asyncio.gather(sony_device_future, media_renderer_future)
        await asyncio.wait(
            [data_found_future, search_finished_future],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if not sony_device_future.done():
            raise SongpalException("Could not find UPnP media server")

        if not media_renderer_future.done():
            raise SongpalException("Could not find UPnP media renderer")

        found_device = sony_device_future.result()
        self._upnp_discovery = found_device
        self._upnp_server = await factory.async_create_device(
            found_device.upnp_location
        )
        self._upnp_renderer = await factory.async_create_device(
            media_renderer_future.result()
        )

        return self._upnp_server, self._upnp_renderer

    async def get_supported_methods(self):
        if self._upnp_discovery is None:
            raise SongpalException("Discovery required")

        if len(self.services) > 0:
            return self.services

        for service_name in self._upnp_discovery.services:
            service = Service(
                service_name,
                self.endpoint + "/" + service_name,
                ProtocolType.XHRPost,
                self.idgen,
            )
            await service.fetch_methods(self.debug)
            self.services[service_name] = service

        return self.services

    async def get_system_info(self) -> Sysinfo:
        if "system" in self.services and self.services["system"].has_method(
            "getSystemInformation"
        ):
            return await super().get_system_info()

        if "system" not in self.services or not self.services["system"].has_method(
            "getNetworkSettings"
        ):
            raise SongpalException("getNetworkSettings not supported")

        if self._upnp_discovery is None:
            raise SongpalException("Discovery required")

        info = await self.services["system"]["getNetworkSettings"](netif="")

        def get_addr(info, iface):
            addr = next((i for i in info if i["netif"] == iface), {}).get("hwAddr")
            return addr.lower().replace("-", ":") if addr else addr

        macAddr = get_addr(info, "eth0")
        wirelessMacAddr = get_addr(info, "wlan0")
        version = self._upnp_discovery.version if self._upnp_discovery else None
        return Sysinfo.make(
            macAddr=macAddr, wirelessMacAddr=wirelessMacAddr, version=version
        )

    async def get_inputs(self) -> List[Input]:
        if "avContent" in self.services and self.services["avContent"].has_method(
            "getCurrentExternalTerminalsStatus"
        ):
            return await super().get_inputs()

        if self._upnp_discovery is None:
            raise SongpalException("Discovery required")

        content_directory = self._upnp_server.service(
            next(
                s for s in self._upnp_discovery.upnp_services if "ContentDirectory" in s
            )
        )

        browse = content_directory.action("Browse")
        filter = (
            "av:BIVL,av:liveType,av:containerClass,dc:title,dc:date,"
            "res,res@duration,res@resolution,upnp:albumArtURI,"
            "upnp:albumArtURI@dlna:profileID,upnp:artist,upnp:album,upnp:genre"
        )
        result = await browse.async_call(
            ObjectID="0",
            BrowseFlag="BrowseDirectChildren",
            Filter=filter,
            StartingIndex=0,
            RequestedCount=25,
            SortCriteria="",
        )

        root_items = didl_lite.from_xml_string(result["Result"])
        input_item = next(
            (
                i
                for i in root_items
                if isinstance(i, didl_lite.Container) and i.title == "Input"
            ),
            None,
        )

        result = await browse.async_call(
            ObjectID=input_item.id,
            BrowseFlag="BrowseDirectChildren",
            Filter=filter,
            StartingIndex=0,
            RequestedCount=25,
            SortCriteria="",
        )

        av_transport = self._upnp_renderer.service(
            next(s for s in self._upnp_renderer.services if "AVTransport" in s)
        )

        media_info = await av_transport.action("GetMediaInfo").async_call(InstanceID=0)
        current_uri = media_info.get("CurrentURI")

        inputs = didl_lite.from_xml_string(result["Result"])

        def is_input_active(input, current_uri):
            if not current_uri:
                return False

            # when input is switched on device, uri can have file:// format
            if current_uri.startswith("file://"):
                # UPnP 'Bluetooth AUDIO' can be file://Bluetooth
                # UPnP 'AUDIO' can be file://Audio
                return current_uri.lower() in "file://" + input.title.lower()

            if current_uri.startswith("local://"):
                # current uri can have additional query params, such as zone
                return input.resources[0].uri in current_uri

        return [
            InputControlUpnp.make(
                title=i.title,
                label=i.title,
                iconUrl="",
                uri=i.resources[0].uri,
                active="active" if is_input_active(i, current_uri) else "",
                avTransport=av_transport,
                uriMetadata=didl_lite.to_xml_string(i).decode("utf-8"),
            )
            for i in inputs
        ]

    async def get_volume_information(self) -> List[Volume]:
        if "audio" in self.services and self.services["audio"].has_method(
            "getVolumeInformation"
        ):
            return await super().get_volume_information()

        if self._upnp_renderer is None:
            raise SongpalException("Discovery required")

        rendering_control_service = self._upnp_renderer.service(
            next(s for s in self._upnp_renderer.services if "RenderingControl" in s)
        )
        volume_result = await rendering_control_service.action("GetVolume").async_call(
            InstanceID=0, Channel="Master"
        )
        mute_result = await rendering_control_service.action("GetMute").async_call(
            InstanceID=0, Channel="Master"
        )

        min_volume = rendering_control_service.state_variables["Volume"].min_value
        max_volume = rendering_control_service.state_variables["Volume"].max_value

        return [
            VolumeControlUpnp.make(
                volume=volume_result["CurrentVolume"],
                mute=mute_result["CurrentMute"],
                minVolume=min_volume,
                maxVolume=max_volume,
                step=1,
                output=None,
                renderingControl=rendering_control_service,
            )
        ]


class DeviceFactory:
    @staticmethod
    async def get(endpoint, force_protocol=None, debug=0, timeout=5):
        device = Device(endpoint, force_protocol=force_protocol, debug=debug)
        try:
            await device.get_supported_methods()
            return device
        except SongpalException as e:
            if e.code == 12 and e.error_message == "getSupportedApiInfo":
                device = await UpnpDevice.create(
                    endpoint,
                    force_protocol=force_protocol,
                    debug=debug,
                    timeout=timeout,
                )
                await device.get_supported_methods()
                return device
            else:
                raise e
