import asyncio
from .conftest import server
from songpal import Device, SongpalException
import pytest


async def test_invalid_endpoint(server):
    dev = Device(endpoint=str(server._root))
    dev.guide_endpoint += "1234"
    with pytest.raises(SongpalException):
        await dev.get_supported_methods()


async def test_fetch_get_supported(server):
    print(server)
    dev = Device(endpoint=str(server._root))

    supported_methods = await dev.get_supported_methods()
    assert len(supported_methods) == 4
