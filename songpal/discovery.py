import logging
from async_upnp_client.discovery import async_discover
from xml import etree
import attr

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

        from async_upnp_client import UpnpFactory
        from async_upnp_client.aiohttp import AiohttpRequester

        async def parse_device(device):
            requester = AiohttpRequester()
            factory = UpnpFactory(requester)

            url = device["location"]
            device = await factory.async_create_device(url)

            if debug > 0:
                print(etree.ElementTree.tostring(device.xml))

            NS = {
                # required for modelNumber ...
                'device': 'urn:schemas-upnp-org:device-1-0',
                'av': 'urn:schemas-sony-com:av',
            }

            model_number = device.xml.find(".//device:modelNumber", NS).text
            info = device.xml.find(".//av:X_ScalarWebAPI_DeviceInfo", NS)
            if not info:
                _LOGGER.error("Unable to find X_ScalaerWebAPI_DeviceInfo")
                return


            endpoint = info.find(".//av:X_ScalarWebAPI_BaseURL", NS).text
            version = info.find(".//av:X_ScalarWebAPI_Version", NS).text
            services = [x.text for x in info.findall(".//av:X_ScalarWebAPI_ServiceType", NS)]

            dev = DiscoveredDevice(name=device.name,
                                   model_number=model_number,
                                   udn=device.udn,
                                   endpoint=endpoint,
                                   version=version,
                                   services=services,
                                   upnp_services=list(device.services.keys()),
                                   upnp_location=url)

            _LOGGER.debug("Discovered: %s" % dev)

            if callback is not None:
                await callback(dev)

        await async_discover(timeout=timeout,
                             service_type=ST,
                             async_callback=parse_device)