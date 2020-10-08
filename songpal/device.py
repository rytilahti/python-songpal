"""Module presenting a single supported device."""
import asyncio
import itertools
import logging
from collections import defaultdict
from typing import Any, Dict, List
from urllib.parse import urlparse

from songpal.common import ProtocolType, SongpalException
from songpal.containers import (
    Content,
    Input,
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
    Zone,
)
from songpal.services import Audio, AVContent, Guide, System

from .notification import ConnectChange, Notification
from .services.service import Service

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

        self.system = None  # type: System
        self.audio = None  # type: Audio
        self.avcontent = None  # type: AVContent

    async def __aenter__(self):
        """Asynchronous context manager, initializes the list of available methods."""
        await self.get_supported_methods()

    async def get_supported_methods(self):
        """Get information about supported methods.

        Calling this as the first thing before doing anything else is
        necessary to fill the available services table.
        """
        guide = Guide(
            "guide",
            endpoint=self.guide_endpoint,
            protocol=ProtocolType.XHRPost,
            idgen=self.idgen,
            debug=self.debug,
        )
        self.services = await guide.get_supported_apis(
            self.endpoint, self.force_protocol
        )
        print(self.services.keys())
        if "system" in self.services:
            self.system = self.services["system"]
        if "audio" in self.services:
            self.audio = self.services["audio"]
        if "avContent" in self.services:
            self.avcontent = self.services["avContent"]

    async def get_power(self) -> Power:
        """Get the device state."""
        return await self.system.get_power()

    async def set_power(self, value: bool):
        """Toggle the device on and off."""
        return await self.system.set_power(value)

    async def get_power_settings(self) -> List[Setting]:
        """Get power settings."""
        return await self.system.get_power_settings()

    async def set_power_settings(self, target: str, value: str) -> None:
        """Set power settings."""
        await self.system.set_power_settings(target, value)

    async def get_googlecast_settings(self) -> List[Setting]:
        """Get Googlecast settings."""
        return await self.system.get_googlecast_settings()

    async def set_googlecast_settings(self, target: str, value: str):
        """Set Googlecast settings."""
        return await self.system.set_googlecast_settings(target, value)

    async def request_settings_tree(self):
        """Get raw settings tree JSON.

        Prefer :func:get_settings: for containerized settings.
        """
        return await self.system.request_settings_tree()

    async def get_settings(self) -> List[SettingsEntry]:
        """Get a list of available settings.

        See :func:request_settings_tree: for raw settings.
        """
        settings = await self.request_settings_tree()
        return [SettingsEntry.make(**x) for x in settings["settings"]]

    async def get_misc_settings(self) -> List[Setting]:
        """Return miscellaneous settings such as name and timezone."""
        return await self.system.get_misc_settings()

    async def set_misc_settings(self, target: str, value: str):
        """Change miscellaneous settings."""
        return await self.system.set_misc_setting(target, value)

    async def get_interface_information(self) -> InterfaceInfo:
        """Return generic product information."""
        return await self.system.get_interface_information()

    async def get_system_info(self) -> Sysinfo:
        """Return system information including mac addresses and current version."""
        return await self.system.get_system_info()

    async def get_sleep_timer_settings(self) -> List[Setting]:
        """Get sleep timer settings."""
        return await self.system.get_sleep_timer_settings()

    async def get_storage_list(self) -> List[Storage]:
        """Return information about connected storage devices."""
        return await self.system.get_storage_list()

    async def get_update_info(self, from_network=True) -> SoftwareUpdateInfo:
        """Get information about updates."""
        return await self.system.get_update_info(from_network=from_network)

    async def activate_system_update(self) -> None:
        """Start a system update if available."""
        return await self.system.activate_system_update()

    async def get_play_info(self) -> PlayInfo:
        """Return  of the device."""
        return await self.avcontent.get_play_info()

    async def get_inputs(self) -> List[Input]:
        """Return list of available outputs."""
        return await self.avcontent.get_inputs()

    async def get_zones(self) -> List[Zone]:
        """Return list of available zones."""
        return await self.avcontent.get_zones()

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
        return await self.avcontent.get_bluetooth_settings()

    async def set_bluetooth_settings(self, target: str, value: str) -> None:
        """Set bluetooth settings."""
        return await self.avcontent.set_bluetooth_setting(target, value)

    async def get_custom_eq(self):
        """Get custom EQ settings."""
        return await self.audio.get_custom_eq()

    async def set_custom_eq(self, target: str, value: str) -> None:
        """Set custom EQ settings."""
        return await self.audio.set_custom_eq(target, value)

    async def get_supported_playback_functions(
        self, uri=""
    ) -> List[SupportedFunctions]:
        """Return list of inputs and their supported functions."""
        return await self.avcontent.get_supported_playback_functions(uri=uri)

    async def get_playback_settings(self) -> List[Setting]:
        """Get playback settings such as shuffle and repeat."""
        return await self.avcontent.get_playback_settings()

    async def set_playback_settings(self, target, value) -> None:
        """Set playback settings such a shuffle and repeat."""
        return await self.avcontent.set_playback_settings(target, value)

    async def get_schemes(self) -> List[Scheme]:
        """Return supported uri schemes."""
        return await self.avcontent.get_schemes()

    async def get_source_list(self, scheme: str = "") -> List[Source]:
        """Return available sources for playback."""
        return await self.avcontent.get_source_list(scheme=scheme)

    async def get_content_count(self, source: str):
        """Return file listing for source."""
        return await self.avcontent.get_content_count(source)

    async def get_contents(self, uri) -> List[Content]:
        """Request content listing recursively for the given URI.

        :param uri: URI for the source.
        :return: List of Content objects.
        """
        return await self.avcontent.get_contents()

    async def get_available_playback_functions(self, output=""):
        """Return available playback functions.

        If no output is given the current is assumed.
        """
        return await self.avcontent.get_available_playback_functions(output=output)

    async def get_volume(self) -> List[Volume]:
        """Get the volume information."""
        return await self.audio.get_volume_information()

    async def get_sound_settings(self, target="") -> List[Setting]:
        """Get the current sound settings.

        :param str target: settings target, defaults to all.
        """
        return await self.audio.get_sound_settings(target)

    async def set_soundfield(self, value):
        """Set soundfield."""
        return await self.audio.set_sound_settings("soundField", value)

    async def set_sound_settings(self, target: str, value: str):
        """Change a sound setting."""
        return await self.audio.set_sound_setting(target, value)

    async def get_speaker_settings(self) -> List[Setting]:
        """Return speaker settings."""
        return await self.audio.get_speaker_settings()

    async def set_speaker_settings(self, target: str, value: str):
        """Set speaker settings."""
        return await self.audio.set_speaker_setting(target, value)

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

        for service in self.services.values():
            tasks.append(
                asyncio.ensure_future(
                    service.listen_all_notifications(handle_notification)
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
        for service in self.services.values():
            await service.stop_listen_notifications()

        return True

    async def get_notifications(self) -> List[Notification]:
        """Get available notifications, which can then be subscribed to.

        Call :func:activate: to enable notifications, and :func:listen_notifications:
        to loop forever for notifications.

        :return: List of Notification objects
        """
        notifications = []
        for service in self.services:
            for notification in self.services[service].notifications:
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
