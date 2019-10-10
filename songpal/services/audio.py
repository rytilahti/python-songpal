from typing import List
import logging

from .service import Service, command
from songpal.containers import Setting, Volume

_LOGGER = logging.getLogger(__name__)


class Audio(Service):
    @command("setSoundSettings")
    async def set_sound_settings(self, settings):
        """Change a sound setting."""
        return await self.set_settings(self["setSoundSettings"], settings)

    async def set_sound_setting(self, target: str, value: str):
        return await self.set_setting(self["setSoundSettings"], target, value)

    @command("getSpeakerSettings")
    async def get_speaker_settings(self) -> List[Setting]:
        """Return speaker settings."""
        return await self.get_settings(self["getSpeakerSettings"], self["setSpeakerSettings"])

    async def set_speaker_setting(self, target: str, value: str):
        """Set speaker settings."""
        return await self.set_setting(self["setSpeakerSettings"], target, value)

    @command("setSpeakerSettings")
    async def set_speaker_settings(self, settings):
        """Change speaker settings, pass a list of setting objects."""
        return await self.set_settings(self["setSpeakerSettings"], settings)

    @command("getVolumeInformation")
    async def get_volume_information(self) -> List[Volume]:
        """Get the volume information."""
        res = await self["getVolumeInformation"]({})
        volume_info = [Volume.make(service=self, **x) for x in res]
        if len(volume_info) < 1:
            _LOGGER.warning("Unable to get volume information")
        elif len(volume_info) > 1:
            _LOGGER.debug("The device seems to have more than one volume setting.")
        return volume_info

    @command("getSoundSettings")
    async def get_sound_settings(self, target="") -> List[Setting]:
        """Get the current sound settings.

        :param str target: settings target, defaults to all.
        """
        return await self.get_settings(self["getSoundSettings"], self["getSoundSettings"], target="")

    async def get_soundfield(self) -> List[Setting]:
        """Get the current sound field settings."""
        _LOGGER.warning("prefer get_sound_setting(s) calls..")
        return await self.get_settings(self["getSoundSettings"], self["setSoundSettings"], "soundField")

    @command(["getCustomEqualizerSettings", "setCustomEqualizerSettings"])
    async def get_custom_eq(self):
        """Get custom EQ settings."""
        return await self.get_settings(self["getCustomEqualizerSettings"], self["setCustomEqualizerSettings"])

    async def set_custom_eq(self, target: str, value: str) -> None:
        """Set custom EQ settings."""
        return await self.set_setting(self["setCustomEqualizerSettings"], target, value)
