import logging

import attr
from async_upnp_client import UpnpFactory
from async_upnp_client.aiohttp import AiohttpRequester

from .containers import make

_LOGGER = logging.getLogger(__name__)


@attr.s
class GroupState:
    make = classmethod(make)

    """{'Discoverable': 'NO',
         'GroupMode': 'IDLE',
         'GroupName': '',
         'GroupSong': 'PUBLIC',
         'GroupState': 'IDLE',
         'MasterSessionID': 0,
         'MasterUUID': '',
         'NumberOfSlaves': 0,
         'PlayingState': 'STOPPED',
         'PowerState': 'ON',
         'RSSIValue': -46,
         'SessionID': 0,
         'SlaveList': '',
         'SlaveNetworkState': '',
         'WiredLinkSpeed': 0,
         'WiredState': 'DOWN',
         'WirelessLinkSpeed': 65,
         'WirelessState': 'UP',
         'WirelessType': '802.11bgn'}
    """

    Discoverable = attr.ib()
    GroupMode = attr.ib()
    GroupName = attr.ib()
    GroupSong = attr.ib()
    GroupState = attr.ib()
    MasterSessionID = attr.ib()
    MasterUUID = attr.ib()
    NumberOfSlaves = attr.ib()
    PlayingState = attr.ib()
    PowerState = attr.ib()
    RSSIValue = attr.ib()
    SessionID = attr.ib()
    SlaveList = attr.ib()
    SlaveNetworkState = attr.ib()
    WiredLinkSpeed = attr.ib()
    WiredState = attr.ib()
    WirelessLinkSpeed = attr.ib()
    WirelessState = attr.ib()
    WirelessType = attr.ib()

    # For GetStateM
    GroupMemoryCount = attr.ib(default=None)
    GroupMemoryUpdateID = attr.ib(default=None)

    def __str__(self):
        s = "Power: %s" % self.PowerState
        s += "\nMode: %s" % self.GroupMode
        if self.GroupMode == "GROUP":
            s += "\nSession ID: %s" % self.SessionID
            s += "\nGroup: %s" % self.GroupName
            s += "\nState: %s" % self.GroupState
            s += "\nSlaves: %s" % self.NumberOfSlaves
            s += "\n  %s" % self.SlaveList

        if self.WiredState != "DOWN":
            s += "\nConnection: Wired"
        if self.WirelessState != "DOWN":
            s += "\nConnection: %s" % self.WirelessType

        return s


class GroupControl:
    def __init__(self, url):
        self.url = url

    async def connect(self):
        requester = AiohttpRequester()
        factory = UpnpFactory(requester)
        device = await factory.async_create_device(self.url)

        self.service = device.service("urn:schemas-sony-com:service:Group:1")
        if not self.service:
            _LOGGER.error("Unable to find group service!")
            return False

        for act in self.service.actions.values():
            _LOGGER.debug(
                "Action: %s (%s)", act, [arg.name for arg in act.in_arguments()]
            )

        return True

        """
        Available actions

        <UpnpService.Action(X_GetDeviceInfo)> ([])
        <UpnpService.Action(X_GetState)> ([])
        <UpnpService.Action(X_GetStateM)> ([])
        <UpnpService.Action(X_SetGroupName)> (['GroupName'])
        <UpnpService.Action(X_ChangeGroupVolume)> (['GroupVolume'])
        <UpnpService.Action(X_GetAllGroupMemory)> ([])
        <UpnpService.Action(X_DeleteGroupMemory)> (['MemoryID'])
        <UpnpService.Action(X_UpdateGroupMemory)> (['MemoryID', 'GroupMode',
            'GroupName', 'SlaveList', 'CodecType', 'CodecBitrate'])
        <UpnpService.Action(X_Start)> (['GroupMode', 'GroupName', 'SlaveList',
            'CodecType', 'CodecBitrate'])
        <UpnpService.Action(X_Entry)> (['MasterSessionID', 'SlaveList'])
        <UpnpService.Action(X_EntryM)> (['MasterSessionID', 'SlaveList'])
        <UpnpService.Action(X_Leave)> (['MasterSessionID', 'SlaveList'])
        <UpnpService.Action(X_LeaveM)> (['MasterSessionID', 'SlaveList'])
        <UpnpService.Action(X_Abort)> (['MasterSessionID'])
        <UpnpService.Action(X_SetGroupMute)> (['GroupMute'])
        <UpnpService.Action(X_SetCodec)> (['CodecType', 'CodecBitrate'])
        <UpnpService.Action(X_GetCodec)> ([])
        <UpnpService.Action(X_Invite)> (['GroupMode', 'GroupName', 'MasterUUID',
            'MasterSessionID'])
        <UpnpService.Action(X_Exit)> (['SlaveSessionID'])
        <UpnpService.Action(X_Play)> (['MasterSessionID'])
        <UpnpService.Action(X_Stop)> (['MasterSessionID'])
        <UpnpService.Action(X_Delegate)> (['GroupMode', 'SlaveList', 'DelegateURI',
            'DelegateURIMetaData'])
        """

    async def call(self, action, **kwargs):
        """Make an action call with given kwargs."""
        act = self.service.action(action)
        _LOGGER.info("Calling %s with %s", action, kwargs)
        res = await act.async_call(**kwargs)

        _LOGGER.info("  Result: %s" % res)

        return res

    async def info(self):
        """Return device info."""
        """
        {'MasterCapability': 9, 'TransportPort': 3975}
        """
        act = self.service.action("X_GetDeviceInfo")
        res = await act.async_call()
        return res

    async def state(self) -> GroupState:
        """Return the current group state"""
        act = self.service.action("X_GetState")
        res = await act.async_call()
        return GroupState.make(**res)

    async def statem(self) -> GroupState:
        """Return the current group state (memory?)."""
        act = self.service.action("X_GetStateM")
        res = await act.async_call()
        return GroupState.make(**res)

    async def get_group_memory(self):
        """Return group memory."""
        # Returns an XML with groupMemoryList
        act = self.service.action("X_GetAllGroupMemory")
        res = await act.async_call()
        return res

    async def update_group_memory(
        self, memory_id, mode, name, slaves, codectype=0x0040, bitrate=0x0003
    ):
        """Update existing memory? Can be used to create new ones, too?"""
        act = self.service.action("X_UpdateGroupMemory")
        res = await act.async_call(
            MemoryID=memory_id,
            GroupMode=mode,
            GroupName=name,
            SlaveList=slaves,
            CodecType=codectype,
            CodecBitrate=bitrate,
        )

        return res

    async def delete_group_memory(self, memory_id):
        """Delete group memory."""
        act = self.service.action("X_DeleteGroupMemory")
        return await act.async_call(MemoryID=memory_id)

    async def get_codec(self):
        """Get codec settings."""
        act = self.service.action("X_GetCodec")
        res = await act.async_call()
        return res

    async def set_codec(self, codectype=0x0040, bitrate=0x0003):
        """Set codec settings."""
        act = self.service.action("X_SetCodec")
        res = await act.async_call(CodecType=codectype, CodecBitrate=bitrate)
        return res

    async def abort(self):
        """Abort current group session."""
        state = await self.state()
        res = await self.call("X_Abort", MasterSessionID=state.MasterSessionID)
        return res

    async def stop(self):
        """Stop playback?"""
        state = await self.state()
        res = await self.call("X_Stop", MasterSessionID=state.MasterSessionID)
        return res

    async def play(self):
        """Start playback?"""
        state = await self.state()
        res = await self.call("X_Play", MasterSessionID=state.MasterSessionID)
        return res

    async def create(self, name, slaves):
        """Create a group."""
        # NOTE: codectype and codecbitrate were simply chosen from an example..
        res = await self.call(
            "X_Start",
            GroupMode="GROUP",
            GroupName=name,
            SlaveList=",".join(slaves),
            CodecType=0x0040,
            CodecBitrate=0x0003,
        )
        return res

    async def add(self, slaves):
        """Add slaves to the current group."""
        state = await self.state()
        res = await self.call(
            "X_Entry", MasterSessionID=state.MasterSessionID, SlaveList=slaves
        )
        return res

    async def add_m(self, slaves):
        """Unknown usage."""
        state = await self.state()
        return await self.call(
            "X_EntryM", MasterSessionID=state.MasterSessionID, SlaveList=slaves
        )

    async def remove(self, slaves):
        """Remove slaves from the current group."""
        state = await self.state()
        return await self.call(
            "X_Leave", MasterSessionID=state.MasterSessionID, SlaveList=slaves
        )

    async def remove_m(self, slaves):
        """Unknown usage."""
        state = await self.state()
        return await self.call(
            "X_LeaveM", MasterSessionID=state.MasterSessionID, SlaveList=slaves
        )

    async def set_mute(self, activate):
        """Set group mute."""
        res = await self.call("X_SetGroupMute", GroupMute=activate)
        return res

    async def set_group_volume(self, volume):
        """Set group volume."""
        res = await self.call("X_ChangeGroupVolume", GroupVolume=volume)
        return res

    async def set_group_name(self, name):
        """Set group name."""
        res = await self.call("X_SetGroupName", GroupName=name)
        return res
