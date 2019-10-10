import pytest
from aiohttp import web
import json
from aiohttp.test_utils import  TestServer, loop_context
from songpal import Device
import logging

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

routes = web.RouteTableDef()



async def get_iface(x):
    _LOGGER.info("got call %s" % x)

@pytest.fixture
def devinfo(shared_datadir):
    devinfo = shared_datadir / "devinfos/HT-XT3.json"

    return devinfo.read_text()


@routes.post('/sony/guide')
async def guide_endpoint(req):

    with open("/home/hass/home-assistant/libs/python-sony/songpal/tests/data/devinfos/HT-XT3.json") as f:
        devinfo = json.load(f)
    _LOGGER.info("Guide endpoint called.")
    return web.json_response(devinfo["supported_methods_response"])


@pytest.fixture
async def server(loop):
    app = web.Application()
    app.router.add_routes(routes)

    server = TestServer(app)


    await server.start_server()
    return server
    #return loop.run_until_complete(aiohttp_client(app))