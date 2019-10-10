from .service import Service, command
from .system import System
from .audio import Audio
from .avcontent import AVContent
import logging

_LOGGER = logging.getLogger(__name__)


class Guide(Service):
    @command("getServiceProtocols")
    async def get_service_protocols(self):
        service_protocols = await self._methods["getServiceProtocols"]()
        return service_protocols

    @command("getSupportedApiInfo")
    async def get_supported_api_info(self):
        return await self._methods["getSupportedApiInfo"]({})

    async def get_supported_apis(self, base_endpoint, force_protocol):
        _LOGGER.info("Versions: %s" % await self.get_versions())
        await self.initialize_methods()

        service_protocols = await self.get_service_protocols()
        print(service_protocols)
        for service_name in service_protocols:
            service_name, protocols = service_name
            _LOGGER.info("Service %s supports %s", service_name, protocols)

        apis = await self.get_supported_api_info()

        supported_services = {
            'guide': self,
            'system': System,
            'audio': Audio,
            'avContent': AVContent,
        }

        initialized_services = {}

        for api in apis:
            service_name = api["service"]
            _LOGGER.info("Got service: %s", service_name)
            if service_name not in supported_services:
                _LOGGER.warning("Service %s is not implemented", service_name)
                continue

            service = await supported_services[service_name].from_payload(
                api, base_endpoint, self.idgen, self.debug, force_protocol
            )

            _LOGGER.info("Initialized service %s", service)

            initialized_services[service_name] = service

        return initialized_services
