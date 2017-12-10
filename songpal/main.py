import ast
import asyncio
import logging
import json
from pprint import pprint as pp

import click
import requests
import upnpclient
from functools import update_wrapper
from lxml import objectify, etree

from songpal import Protocol


def coro(f):
    """https://github.com/pallets/click/issues/85#issuecomment-43378930"""
    f = asyncio.coroutine(f)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))

    return update_wrapper(wrapper, f)


async def traverse_settings(dev, module, settings, depth=0):
    """Goes through all """
    for setting in settings:
        if setting.is_directory:
            print("%s%s (%s)" % (depth * ' ', setting.title, module))
            return await traverse_settings(dev, module,
                                           setting.settings, depth + 2)
        else:
            print_settings([await setting.get_value(dev)], depth=depth)


def print_settings(settings, depth=0):
    """Print all available settings of the device."""
    for setting in settings:
        cur = setting.currentValue
        print("%s* %s (%s, value: %s, type: %s)" % (' ' * depth,
                                                    setting.title,
                                                    setting.target,
                                                    click.style(cur,
                                                                bold=True),
                                                    setting.type))
        for opt in setting.candidate:
            click.echo(
                click.style("%s  - %s (%s)" % (' ' * depth,
                                               opt.title,
                                               opt.value),
                            bold=opt.value == cur))


logging.getLogger("websockets.protocol").setLevel(logging.WARNING)

pass_dev = click.make_pass_decorator(Protocol)


@click.group(invoke_without_command=True)
@click.option("--endpoint", envvar="SONGPAL_ENDPOINT")
@click.option('-d', '--debug', default=False, count=True)
@click.pass_context
@click.version_option()
@coro
async def cli(ctx, endpoint, debug):
    lvl = logging.INFO
    if debug:
        lvl = logging.DEBUG
    logging.basicConfig(level=lvl)

    if ctx.invoked_subcommand == "discover":
        ctx.obj = "discover"
        return

    logging.debug("Using endpoint %s", endpoint)
    x = Protocol(endpoint, debug=debug)
    try:
        await x.get_supported_methods()
    except requests.exceptions.ConnectionError as ex:
        click.echo("Unable to get supported methods: %s" % ex)
        return
    ctx.obj = x

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)


@cli.command()
@pass_dev
@coro
async def status(dev: Protocol):
    """Display status information."""
    power = await dev.get_power()
    click.echo(click.style("%s" % power, bold=power))

    vol = await dev.get_volume_information()
    click.echo(vol.pop())

    play_info = await dev.get_play_info()
    if not play_info.is_idle:
        click.echo("Playing %s" % play_info)
    else:
        click.echo("Not playing any media")

    outs = await dev.get_outputs()
    for out in outs:
        if out.active:
            click.echo("Active output: %s" % out)

    sysinfo = await dev.get_system_info()
    click.echo("System information: %s" % sysinfo)


@cli.command()
@coro
async def discover():
    """Discover supported devices."""
    TIMEOUT = 3

    click.echo("Discovering for %s seconds" % TIMEOUT)
    devices = upnpclient.discover(TIMEOUT)
    for dev in devices:
        if 'ScalarWebAPI' in dev.service_map:
            model = dev.model_name
            model_number = dev.model_number

            pretty_name = "%s - %s" % (model, model_number)

            root = objectify.fromstring(etree.tostring(dev._root_xml))
            device = root["device"]
            info = device["{urn:schemas-sony-com:av}X_ScalarWebAPI_DeviceInfo"]
            endpoint = info["X_ScalarWebAPI_BaseURL"].text
            version = info["X_ScalarWebAPI_Version"].text
            services = info["X_ScalarWebAPI_ServiceList"].iterchildren()

            click.echo(click.style("Found %s" % pretty_name, bold=True))
            click.echo("* API version: %s" % version)
            click.echo("* Endpoint: %s" % endpoint)

            click.echo("* Services:")
            for serv in services:
                click.echo("  - Service: %s" % serv.text)


@cli.command()
@click.argument("cmd", required=False)
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def power(dev: Protocol, cmd, target, value):
    """Turn on and off, control power settings.

    Accepts commands 'on', 'off', and 'settings'.
    """
    if cmd == "on":
        await dev.set_power(True)
    elif cmd == "off":
        await dev.set_power(False)
    elif cmd == "settings":
        settings = await dev.get_power_settings()
        print_settings(settings)
    elif cmd == "set" and target and value:
        click.echo(await dev.set_power_settings(target, value))
    else:
        power = await dev.get_power()
        click.echo(click.style(str(power), bold=power))


@cli.command()
@click.argument("output", required=False)
@pass_dev
@coro
async def output(dev: Protocol, output):
    """Get and change outputs."""
    outs = await dev.get_outputs()
    if output:
        click.echo("Activating %s" % output)
        try:
            out = next((x for x in outs if x.title == output))
            await out.activate()
        except StopIteration:
            click.echo("Unable to find output %s" % output)
            return
    else:
        click.echo("Outputs:")
        for out in outs:
            act = False
            if out.active:
                act = True
            click.echo("  * " + click.style(str(out), bold=act))


@cli.command()
@pass_dev
@coro
async def googlecast(dev: Protocol):
    """Return Googlecast settings."""
    print_settings(await dev.get_wutang())


@cli.command()
@click.argument("source", default='storage', required=False)
@pass_dev
@coro
async def source(dev: Protocol, source):
    """List contents?"""
    sources = await dev.get_source_list(source)
    for src in sources:
        click.echo(src)
        click.echo("%s" % await dev.get_content_count(src.source))
        for content in await dev.get_contents(src.source):
            click.echo("   %s\n\t%s" % (content.title, content.uri))


@cli.command()
@click.argument("volume", required=False)
@pass_dev
@coro
async def volume(dev: Protocol, volume):
    """Get and set the volume settings.

    Passing 'mute' as new volume will mute the volume,
    'unmute' removes it.
    """
    vol = await dev.get_volume_information()
    vol = vol.pop()
    if volume and volume == "mute":
        click.echo("Muting")
        await vol.set_mute(True)
    elif volume and volume == "unmute":
        click.echo("Unmuting")
        await vol.set_mute(False)
    elif volume:
        click.echo("Setting volume to %s" % volume)
        await vol.set_volume(volume)

    click.echo(vol)


@cli.command()
@pass_dev
@coro
async def schemes(dev: Protocol):
    """Print supported uri schemes."""
    schemes = await dev.get_schemes()
    for scheme in schemes:
        click.echo(scheme)


@cli.command()
@pass_dev
@coro
async def check_update(dev: Protocol):
    """Print out update information."""
    click.echo(await dev.get_update_info())


@cli.command()
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def bluetooth(dev: Protocol, target, value):
    """Get or set bluetooth settings."""
    if target and value:
        await dev.set_bluetooth_settings(target, value)

    print_settings(await dev.get_bluetooth_settings())


@cli.command()
@pass_dev
@coro
async def sysinfo(dev: Protocol):
    """Print out system information (version, MAC addrs)."""
    click.echo(await dev.get_system_info())
    click.echo(await dev.get_interface_information())


@cli.command()
@pass_dev
@coro
async def misc(dev: Protocol):
    """Print miscellaneous settings."""
    print_settings(await dev.get_misc_settings())


@cli.command()
@pass_dev
@coro
async def settings(dev: Protocol):
    """Print out all possible settings."""
    settings_tree = await dev.get_settings()

    for module in settings_tree:
        await traverse_settings(dev, module.usage, module.settings)


@cli.command()
@pass_dev
@coro
async def storage(dev: Protocol):
    """Print storage information."""
    storages = await dev.get_storage_list()
    for storage in storages:
        click.echo(storage)


@cli.command()
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def sound(dev: Protocol, target, value):
    """Get or set sound settings."""
    if target and value:
        click.echo("Setting %s to %s" % (target, value))
        click.echo(await dev.set_sound_settings(target, value))

    print_settings(await dev.get_sound_settings())


@cli.command()
@pass_dev
@coro
async def eq(dev: Protocol):
    """Return EQ information."""
    click.echo(await dev.get_custom_eq())


@cli.command()
@click.argument("cmd", required=False)
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def playback(dev: Protocol, cmd, target, value):
    """Get and set playback settings, e.g. repeat and shuffle.."""
    if target and value:
        dev.set_playback_settings(target, value)
    if cmd == "support":
        click.echo("Supported playback functions:")
        supported = await dev.get_supported_playback_functions('storage:usb1')
        for i in supported:
            print(i)
    elif cmd == "settings":
        print_settings(await dev.get_playback_settings())
        # click.echo("Playback functions:")
        # funcs = await dev.get_available_playback_functions()
        # print(funcs)
    else:
        click.echo("Currently playing: %s" % await dev.get_play_info())


@cli.command()
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def speaker(dev: Protocol, target, value):
    """Get and set external speaker settings."""
    if target and value:
        click.echo("Setting %s to %s" % (target, value))
        await dev.set_speaker_settings(target, value)

    pp(await dev.get_speaker_settings())


@cli.command()
@pass_dev
@coro
async def notifications(dev: Protocol):
    """Get list of available notifications.
    Useful for developers only."""
    click.echo(await dev.get_notifications())


@cli.command()
@pass_dev
@coro
async def sleep(dev: Protocol):
    """Return sleep settings."""
    click.echo(await dev.get_sleep_timer_settings())


@cli.command()
@pass_dev
def list_all(dev):
    """List all available API calls."""
    for name, service in dev.services.items():
        click.echo(click.style("\nService %s" % name, bold=True))
        for api in service.methods:
            click.echo("  %s" % api)


@cli.command()
@click.argument('service', required=True)
@click.argument('method')
@click.argument('parameters', required=False, default=None)
@pass_dev
@coro
async def command(dev, service, method, parameters):
    """Run a raw command."""
    params = None
    if parameters is not None:
        params = ast.literal_eval(parameters)
    click.echo("Calling %s.%s with params %s" % (service, method, params))
    res = await dev.raw_command(service, method, params)
    click.echo(res)


@cli.command()
@pass_dev
@coro
async def dump_devinfo(dev: Protocol):
    """Dumps information for developers."""
    import attr
    methods = await dev.get_supported_methods()
    res = {'supported_methods': {k: v.asdict() for k, v in methods.items()},
           'settings': [attr.asdict(x) for x in await dev.get_settings()],
           'sysinfo': attr.asdict(await dev.get_system_info()),
           'interface_info': attr.asdict(await dev.get_interface_information())}
    print(json.dumps(res))

if __name__ == "__main__":
    cli()
