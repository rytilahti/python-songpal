from songpal import Discover
from songpal.discovery import DiscoveredDevice
from async_upnp_client import UpnpFactory
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock
import pytest
import os

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


async def async_magic():
    pass

MagicMock.__await__ = lambda x: async_magic().__await__()


@pytest.mark.asyncio
async def test_handle_discovered_device(mocker):
    mocker.patch('asyncio.sleep')
    mock_device = MagicMock(spec=dict)

    d = {
        'location': 'x'
    }

    mock_device.__getitem__.side_effect = d.__getitem__

    async def xml():
        return ET.parse(os.path.join(THIS_DIR, 'disco.xml'))

    mocker.patch.object(UpnpFactory, 'async_create_service')

    get_xml = mocker.patch.object(UpnpFactory, "_async_get_url_xml", autospec=True)
    get_xml.return_value = xml()

    device_discovered = False

    async def discovered_device(dev: DiscoveredDevice):
        nonlocal device_discovered

        assert dev.name is not None
        assert dev.model_number is not None
        assert dev.udn is not None
        assert len(dev.services) > 0
        assert dev.endpoint is not None

        device_discovered = True

    await Discover._handle_discovered_device(mock_device, callback=discovered_device)

    assert device_discovered
