import attr
import logging

from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client import UpnpFactory

_LOGGER = logging.getLogger(__name__)


from .containers import make

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

        self.service = device.service('urn:schemas-sony-com:service:Group:1')
        if not self.service:
            _LOGGER.error("Unable to find group service!")
            return False

        for act in self.service.actions.values():
            _LOGGER.debug("Action: %s (%s)", act, [arg.name for arg in act.in_arguments()])

        return True

        """
        Available actions

        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_GetDeviceInfo)> ([])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_GetState)> ([])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_GetStateM)> ([])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_SetGroupName)> (['GroupName'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_ChangeGroupVolume)> (['GroupVolume'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_GetAllGroupMemory)> ([])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_DeleteGroupMemory)> (['MemoryID'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_UpdateGroupMemory)> (['MemoryID', 'GroupMode', 'GroupName', 'SlaveList', 'CodecType', 'CodecBitrate'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Start)> (['GroupMode', 'GroupName', 'SlaveList', 'CodecType', 'CodecBitrate'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Entry)> (['MasterSessionID', 'SlaveList'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_EntryM)> (['MasterSessionID', 'SlaveList'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Leave)> (['MasterSessionID', 'SlaveList'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_LeaveM)> (['MasterSessionID', 'SlaveList'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Abort)> (['MasterSessionID'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_SetGroupMute)> (['GroupMute'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_SetCodec)> (['CodecType', 'CodecBitrate'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_GetCodec)> ([])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Invite)> (['GroupMode', 'GroupName', 'MasterUUID', 'MasterSessionID'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Exit)> (['SlaveSessionID'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Play)> (['MasterSessionID'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Stop)> (['MasterSessionID'])
        INFO:songpal.upnpctl:Action: <UpnpService.Action(X_Delegate)> (['GroupMode', 'SlaveList', 'DelegateURI', 'DelegateURIMetaData'])

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

    async def statem(self):
        """Return the current group state (memory?)."""
        act = self.service.action("X_GetStateM")
        res = await act.async_call()
        return GroupState.make(**res)

    async def get_group_memory(self, result):
        """Return group memory."""
        # Returns an XML with groupMemoryList
        # X_DeleteGroupMemory)> (['MemoryID'])
        # X_UpdateGroupMemory)> (['MemoryID', 'GroupMode', 'GroupName', 'SlaveList', 'CodecType', 'CodecBitrate'])
        act = self.service.action("X_GetAllGroupMemory")
        res = await act.async_call()
        return res

    async def abort(self):
        """Abort current group session."""
        state = await self.state()
        res = await self.call("X_Abort", MasterSessionID=state.SessionID)
        return res

    async def create(self, name, slaves):
        """Create a group."""
        # NOTE: codectype and codecbitrate were simply chosen from an example..
        res = await self.call("X_Start", GroupMode="GROUP",
                              GroupName=name,
                              SlaveList=",".join(slaves),
                              CodecType=0x0040,
                              CodecBitrate=0x0003)
        return res

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
