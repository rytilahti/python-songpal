from typing import List

from .service import Service, command, ServiceImplementation
from ..containers import Power, Setting, InterfaceInfo, Sysinfo, Storage, SoftwareUpdateInfo


_implemented_commands = set()


class System(Service, metaclass=ServiceImplementation):
    """Implementation of songpal's system service."""

    @command("getPowerStatus")
    async def get_power(self) -> Power:
        """Get the device state."""
        res = await self["getPowerStatus"]()
        return Power.make(**res)

    @command("setPowerStatus")
    async def set_power(self, value: bool):
        """Toggle the device on and off."""
        if value:
            status = "active"
        else:
            status = "off"
        # TODO WoL works when quickboot is not enabled
        return await self["setPowerStatus"](status=status)

    @command("getPowerSettings")
    async def get_power_settings(self) -> List[Setting]:
        """Get power settings."""
        return [
            Setting.make(**x)
            for x in await self["getPowerSettings"]({})
        ]

    @command("setPowerSettings")
    async def set_power_settings(self, target: str, value: str) -> None:
        """Set power settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self["setPowerSettings"](params)

    @command("getWuTangInfo")
    async def get_googlecast_settings(self) -> List[Setting]:
        """Get Googlecast settings."""
        return [
            Setting.make(**x)
            for x in await self["getWuTangInfo"]({})
        ]

    @command("setWuTangInfo")
    async def set_googlecast_settings(self, target: str, value: str):
        """Set Googlecast settings."""
        params = {"settings": [{"target": target, "value": value}]}
        return await self["setWuTangInfo"](params)

    @command("getSettingsTree")
    async def request_settings_tree(self):
        """Get raw settings tree JSON.

        Prefer :func:get_settings: for containerized settings.
        """
        return await self["getSettingsTree"](usage="")

    @command("getDeviceMiscSettings")
    async def get_misc_settings(self) -> List[Setting]:
        """Return miscellaneous settings such as name and timezone."""
        return await self.get_settings(self["getDeviceMiscSettings"], self["setDeviceMiscSettings"], target="")

    @command("setDeviceMiscSettings")
    async def set_misc_setting(self, target: str, value: str):
        """Change miscellaneous settings."""
        return await self.set_setting(self["setDeviceMiscSetting"], target, value)

    @command("getInterfaceInformation")
    async def get_interface_information(self) -> InterfaceInfo:
        """Return generic product information."""
        iface = await self["getInterfaceInformation"]()
        return InterfaceInfo.make(**iface)

    @command("getSystemInformation")
    async def get_system_info(self) -> Sysinfo:
        """Return system information including mac addresses and current version."""
        return Sysinfo.make(**await self["getSystemInformation"]())

    @command("getSleepTimerSettings")
    async def get_sleep_timer_settings(self) -> List[Setting]:
        """Get sleep timer settings."""
        return await self.get_settings(self["getSleepTimerSettings"], self["setSleepTimerSettings"])

    @command("getStorageList")
    async def get_storage_list(self) -> List[Storage]:
        """Return information about connected storage devices."""
        return [
            Storage.make(**x)
            for x in await self["getStorageList"]({})
        ]

    @command("getRemoteControllerInfo")
    async def get_remote_controls(self):
        raise NotImplementedError()

    @command("getSWUpdateInfo")
    async def get_update_info(self, from_network=True) -> SoftwareUpdateInfo:
        """Get information about updates."""
        if from_network:
            from_network = "true"
        else:
            from_network = "false"
        # from_network = ""
        info = await self["getSWUpdateInfo"](network=from_network)
        return SoftwareUpdateInfo.make(**info, service=self)

    async def activate_system_update(self) -> None:
        """Start a system update if available."""
        return await self.get_update_info(from_network=True).update()
        raise Exception("call softwareupdateinfo.update()")
