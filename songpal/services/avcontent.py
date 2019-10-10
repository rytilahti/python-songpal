from typing import List

from .service import Service, command
from songpal.common import SongpalException
from songpal.containers import Input, Zone, Content, Source, Scheme, Setting, SupportedFunctions, ContentInfo, PlayInfo


class AVContent(Service):
    @command("getCurrentExternalTerminalsStatus")
    async def get_inputs(self) -> List[Input]:
        """Return list of available outputs."""
        res = await self["getCurrentExternalTerminalsStatus"]()
        return [Input.make(service=self, **x) for x in res if 'meta:zone:output' not in x['meta']]

    @command("getCurrentExternalTerminalsStatus")
    async def get_zones(self) -> List[Zone]:
        """Return list of available zones."""
        res = await self["getCurrentExternalTerminalsStatus"]()
        zones = [Zone.make(service=self, **x) for x in res if 'meta:zone:output' in x['meta']]
        if not zones:
            raise SongpalException("Device has no zones")
        return zones

    @command(["getPlaybackModeSettings", "setPlaybackModeSettings"])
    async def get_playback_settings(self) -> List[Setting]:
        """Get playback settings such as shuffle and repeat."""
        return await self.get_settings(self["getPlaybackModeSettings"], self["setPlaybackModeSettings"])

    async def set_playback_settings(self, target, value) -> None:
        """Set playback settings such a shuffle and repeat."""
        return await self.set_setting(self["setPlaybackModeSettings"], target, value)

    @command(["getBluetoothSettings", "setBluetoothSettings"])
    async def get_bluetooth_settings(self) -> List[Setting]:
        """Get bluetooth settings."""
        return await self.get_settings(self["getBluetoothSettings"], self["setBluetoothSettings"])

    async def set_bluetooth_setting(self, target: str, value: str) -> None:
        """Set bluetooth settings."""
        return await self.set_setting(self["setBluetoothSetting"], target, value)

    @command("getSupportedPlaybackFunction")
    async def get_supported_playback_functions(
        self, uri=""
    ) -> List[SupportedFunctions]:
        """Return list of inputs and their supported functions."""
        return [
            SupportedFunctions.make(**x)
            for x in await self["getSupportedPlaybackFunction"](
                uri=uri
            )
        ]

    @command("getSchemeList")
    async def get_schemes(self) -> List[Scheme]:
        """Return supported uri schemes."""
        return [
            Scheme.make(**x, sources_getter=self["getSourceList"])
            for x in await self["getSchemeList"]()
        ]

    @command("getSourceList")
    async def get_source_list(self, scheme: str = "") -> List[Source]:
        """Return available sources for playback."""
        for scheme in await self.get_schemes():
            if scheme.scheme == scheme:
                return await scheme.get_sources()

    @command("getContentCount")
    async def get_content_count(self, source: str):
        """Return file listing for source."""
        params = {"uri": source, "type": None, "target": "all", "view": "flat"}
        return ContentInfo.make(
            **await self["getContentCount"](params)
        )

    @command("getContentList")
    async def get_contents(self, uri) -> List[Content]:
        """Request content listing recursively for the given URI.

        :param uri: URI for the source.
        :return: List of Content objects.
        """
        contents = [
            Content.make(**x)
            for x in await self["getContentList"](uri=uri)
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

    @command("getAvailablePlaybackFunction")
    async def get_available_playback_functions(self, output=""):
        """Return available playback functions.

        If no output is given the current is assumed.
        """
        await self["getAvailablePlaybackFunction"](output=output)

    @command("getPlayingContentInfo")
    async def get_play_info(self) -> PlayInfo:
        """Return  of the device."""
        info = await self["getPlayingContentInfo"]({})
        return PlayInfo.make(**info.pop())
