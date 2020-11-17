import logging
from xml import etree

import attr
from async_upnp_client import UpnpFactory
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.search import async_search

_LOGGER = logging.getLogger(__name__)


@attr.s
class DiscoveredDevice:
    name = attr.ib()
    model_number = attr.ib()
    udn = attr.ib()
    services = attr.ib()
    upnp_location = attr.ib()
    endpoint = attr.ib()
    version = attr.ib()
    upnp_services = attr.ib()


class Discover:
    ST = "urn:schemas-sony-com:service:ScalarWebAPI:1"

    @staticmethod
    async def discover(timeout, debug=0, callback=None):
        """Discover supported devices."""

        _LOGGER.info("Discovering for %s seconds" % timeout)

        async def parse(device):
            dev = Discover.parse_device(device, debug=debug)
            _LOGGER.debug("Discovered: %s" % dev)
            if callback is not None:
                await callback(dev)

        await async_search(
            timeout=timeout, service_type=Discover.ST, async_callback=parse
        )

    @staticmethod
    async def parse_device(device, debug=0):
        requester = AiohttpRequester()
        factory = UpnpFactory(requester)

        url = device["location"]
        device = await factory.async_create_device(url)

        if debug > 0:
            print(etree.ElementTree.tostring(device.xml).decode())

        NS = {"av": "urn:schemas-sony-com:av"}

        info = device.xml.find(".//av:X_ScalarWebAPI_DeviceInfo", NS)
        if not info:
            _LOGGER.error("Unable to find X_ScalaerWebAPI_DeviceInfo")
            return

        endpoint = info.find(".//av:X_ScalarWebAPI_BaseURL", NS).text
        version = info.find(".//av:X_ScalarWebAPI_Version", NS).text
        services = [
            x.text for x in info.findall(".//av:X_ScalarWebAPI_ServiceType", NS)
        ]

        return DiscoveredDevice(
            name=device.name,
            model_number=device.model_number,
            udn=device.udn,
            endpoint=endpoint,
            version=version,
            services=services,
            upnp_services=list(device.services.keys()),
            upnp_location=url,
        )
