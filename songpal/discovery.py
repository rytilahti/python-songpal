import logging
from xml import etree

import attr
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.client_factory import UpnpFactory
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
    @staticmethod
    async def discover(timeout, debug=0, callback=None):
        """Discover supported devices."""
        ST = "urn:schemas-sony-com:service:ScalarWebAPI:1"
        _LOGGER.info("Discovering for %s seconds" % timeout)

        async def parse_device(device):
            requester = AiohttpRequester()
            factory = UpnpFactory(requester)

            url = device["location"]
            try:
                device = await factory.async_create_device(url)
            except Exception as ex:
                _LOGGER.error(
                    "Unable to download the device description file from %s: %s",
                    url,
                    ex,
                )
                return

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

            dev = DiscoveredDevice(
                name=device.name,
                model_number=device.model_number,
                udn=device.udn,
                endpoint=endpoint,
                version=version,
                services=services,
                upnp_services=list(device.services.keys()),
                upnp_location=url,
            )

            _LOGGER.debug("Discovered: %s" % dev)

            if callback is not None:
                await callback(dev)

        await async_search(
            timeout=timeout, search_target=ST, async_callback=parse_device
        )
