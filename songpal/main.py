"""Click-based interface for Songpal."""
import ast
import asyncio
from functools import update_wrapper
import json
import logging
import sys

import click
from lxml import etree, objectify
import requests

from songpal import Device, SongpalException
from songpal.common import ProtocolType
from songpal.containers import Setting
import upnpclient


def err(msg):
    """Pretty-print an error."""
    click.echo(click.style(msg, fg="red", bold=True))


def coro(f):
    """Run a coroutine and handle possible errors for the click cli.

    Source https://github.com/pallets/click/issues/85#issuecomment-43378930
    """
    f = asyncio.coroutine(f)

    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        except SongpalException as ex:
            err("Error: %s" % ex)
            raise ex

    return update_wrapper(wrapper, f)


async def traverse_settings(dev, module, settings, depth=0):
    """Print all available settings."""
    for setting in settings:
        if setting.is_directory:
            print("%s%s (%s)" % (depth * " ", setting.title, module))
            return await traverse_settings(dev, module, setting.settings, depth + 2)
        else:
            print_settings([await setting.get_value(dev)], depth=depth)


def print_settings(settings, depth=0):
    """Print all available settings of the device."""
    # handle the case where a single setting is passed
    if isinstance(settings, Setting):
        settings = [settings]
    for setting in settings:
        cur = setting.currentValue
        print(
            "%s* %s (%s, value: %s, type: %s)"
            % (
                " " * depth,
                setting.title,
                setting.target,
                click.style(cur, bold=True),
                setting.type,
            )
        )
        for opt in setting.candidate:
            if not opt.isAvailable:
                logging.debug("Unavailable setting %s", opt)
                continue
            click.echo(
                click.style(
                    "%s  - %s (%s)" % (" " * depth, opt.title, opt.value),
                    bold=opt.value == cur,
                )
            )


pass_dev = click.make_pass_decorator(Device)


@click.group(invoke_without_command=False)
@click.option("--endpoint", envvar="SONGPAL_ENDPOINT", required=False)
@click.option("-d", "--debug", default=False, count=True)
@click.option("--post", is_flag=True, required=False)
@click.option("--websocket", is_flag=True, required=False)
@click.pass_context
@click.version_option()
@coro
async def cli(ctx, endpoint, debug, websocket, post):
    """Click entrypoint."""
    lvl = logging.INFO
    if debug:
        lvl = logging.DEBUG
        click.echo("Setting debug level to %s" % debug)
    logging.basicConfig(level=lvl)

    if ctx.invoked_subcommand == "discover":
        ctx.obj = {"debug": debug}
        return

    if endpoint is None:
        err("Endpoint is required except when with 'discover'!")
        return

    protocol = None
    if post and websocket:
        err("You can force either --post or --websocket")
        return
    elif websocket:
        protocol = ProtocolType.WebSocket
    elif post:
        protocol = ProtocolType.XHRPost

    logging.debug("Using endpoint %s", endpoint)
    x = Device(endpoint, force_protocol=protocol, debug=debug)
    try:
        await x.get_supported_methods()
    except requests.exceptions.ConnectionError as ex:
        err("Unable to get supported methods: %s" % ex)
        sys.exit(-1)
    ctx.obj = x

    # this causes RuntimeError: This event loop is already running
    # if ctx.invoked_subcommand is None:
    # ctx.invoke(status)


@cli.command()
@pass_dev
@coro
async def status(dev: Device):
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

    outs = await dev.get_inputs()
    for out in outs:
        if out.active:
            click.echo("Active output: %s" % out)

    sysinfo = await dev.get_system_info()
    click.echo("System information: %s" % sysinfo)


@cli.command()
@coro
@click.pass_context
async def discover(ctx):
    """Discover supported devices."""
    TIMEOUT = 3
    debug = 0
    if ctx.obj:
        debug = ctx.obj["debug"] or 0
    click.echo("Discovering for %s seconds" % TIMEOUT)
    devices = upnpclient.discover(TIMEOUT)
    for dev in devices:
        if "ScalarWebAPI" in dev.service_map:
            if debug:
                print(etree.tostring(dev._root_xml, pretty_print=True).decode())
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
async def power(dev: Device, cmd, target, value):
    """Turn on and off, control power settings.

    Accepts commands 'on', 'off', and 'settings'.
    """
    async def try_turn(cmd):
        state = True if cmd == "on" else False
        try:
            return await dev.set_power(state)
        except SongpalException as ex:
            if ex.code == 3:
                err("The device is already %s." % cmd)
            else:
                raise ex

    if cmd == "on" or cmd == "off":
        click.echo(await try_turn(cmd))
    elif cmd == "settings":
        settings = await dev.get_power_settings()
        print_settings(settings)
    elif cmd == "set" and target and value:
        click.echo(await dev.set_power_settings(target, value))
    else:
        power = await dev.get_power()
        click.echo(click.style(str(power), bold=power))


@cli.command()
@click.argument("input", required=False)
@pass_dev
@coro
async def input(dev: Device, input):
    """Get and change outputs."""
    inputs = await dev.get_inputs()
    if input:
        click.echo("Activating %s" % input)
        try:
            input = next((x for x in inputs if x.title == input))
            await input.activate()
        except StopIteration:
            click.echo("Unable to find input %s" % input)
            return
    else:
        click.echo("Inputs:")
        for input in inputs:
            act = False
            if input.active:
                act = True
            click.echo("  * " + click.style(str(input), bold=act))
            for out in input.outputs:
                click.echo("    - %s" % out)


@cli.command()
@pass_dev
@coro
async def googlecast(dev: Device):
    """Return Googlecast settings."""
    print_settings(await dev.get_wutang())


@cli.command()
@click.argument("scheme", required=False)
@pass_dev
@coro
async def source(dev: Device, scheme):
    """List available sources.

    If no `scheme` is given, will list sources for all sc hemes.
    """
    if scheme is None:
        schemes = await dev.get_schemes()
        schemes = [scheme.scheme for scheme in schemes]  # noqa: T484
    else:
        schemes = [scheme]

    for schema in schemes:
        try:
            sources = await dev.get_source_list(schema)
        except SongpalException as ex:
            click.echo("Unable to get sources for %s" % schema)
            continue
        for src in sources:
            click.echo(src)
            if src.isBrowsable:
                try:
                    count = await dev.get_content_count(src.source)
                    if count.count > 0:
                        click.echo("  %s" % count)
                        for content in await dev.get_contents(src.source):
                            click.echo("   %s\n\t%s" % (content.title, content.uri))
                    else:
                        click.echo("  No content to list.")
                except SongpalException as ex:
                    click.echo("  %s" % ex)


@cli.command()
@click.option("--output", type=str, required=False)
@click.argument("volume", required=False)
@pass_dev
@coro
async def volume(dev: Device, volume, output):
    """Get and set the volume settings.

    Passing 'mute' as new volume will mute the volume,
    'unmute' removes it.
    """
    vol = None
    vol_controls = await dev.get_volume_information()
    if output is not None:
        click.echo("Using output: %s" % output)
        for v in vol_controls:
            if v.output == output:
                vol = v
                break
    else:
        vol = vol_controls.pop()

    if vol is None:
        err("Unable to find volume controller: %s" % output)
        return

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
async def schemes(dev: Device):
    """Print supported uri schemes."""
    schemes = await dev.get_schemes()
    for scheme in schemes:
        click.echo(scheme)


@cli.command()
@click.option("--internet", is_flag=True, default=True)
@click.option("--update", is_flag=True, default=False)
@pass_dev
@coro
async def check_update(dev: Device, internet: bool, update: bool):
    """Print out update information."""
    if internet:
        print("Checking updates from network")
    else:
        print("Not checking updates from internet")
    update_info = await dev.get_update_info(from_network=internet)
    if not update_info.isUpdatable:
        click.echo("No updates available.")
        return
    if not update:
        click.echo("Update available: %s" % update_info)
        click.echo("Use --update to activate update!")
    else:
        click.echo("Activating update, please be seated.")
        res = await dev.activate_system_update()
        click.echo("Update result: %s" % res)


@cli.command()
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def bluetooth(dev: Device, target, value):
    """Get or set bluetooth settings."""
    if target and value:
        await dev.set_bluetooth_settings(target, value)

    print_settings(await dev.get_bluetooth_settings())


@cli.command()
@pass_dev
@coro
async def sysinfo(dev: Device):
    """Print out system information (version, MAC addrs)."""
    click.echo(await dev.get_system_info())
    click.echo(await dev.get_interface_information())


@cli.command()
@pass_dev
@coro
async def misc(dev: Device):
    """Print miscellaneous settings."""
    print_settings(await dev.get_misc_settings())


@cli.command()
@pass_dev
@coro
async def settings(dev: Device):
    """Print out all possible settings."""
    settings_tree = await dev.get_settings()

    for module in settings_tree:
        await traverse_settings(dev, module.usage, module.settings)


@cli.command()
@pass_dev
@coro
async def storage(dev: Device):
    """Print storage information."""
    storages = await dev.get_storage_list()
    for storage in storages:
        click.echo(storage)


@cli.command()
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def sound(dev: Device, target, value):
    """Get or set sound settings."""
    if target and value:
        click.echo("Setting %s to %s" % (target, value))
        click.echo(await dev.set_sound_settings(target, value))

    print_settings(await dev.get_sound_settings())


@cli.command()
@pass_dev
@click.argument("soundfield", required=False)
@coro
async def soundfield(dev: Device, soundfield: str):
    """Get or set sound field."""
    if soundfield is not None:
        await dev.set_sound_settings("soundField", soundfield)
    soundfields = await dev.get_sound_settings("soundField")
    print(await dev.get_soundfield())
    print_settings(soundfields)


@cli.command()
@pass_dev
@coro
async def eq(dev: Device):
    """Return EQ information."""
    click.echo(await dev.get_custom_eq())


@cli.command()
@click.argument("cmd", required=False)
@click.argument("target", required=False)
@click.argument("value", required=False)
@pass_dev
@coro
async def playback(dev: Device, cmd, target, value):
    """Get and set playback settings, e.g. repeat and shuffle.."""
    if target and value:
        dev.set_playback_settings(target, value)
    if cmd == "support":
        click.echo("Supported playback functions:")
        supported = await dev.get_supported_playback_functions("storage:usb1")
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
async def speaker(dev: Device, target, value):
    """Get and set external speaker settings."""
    if target and value:
        click.echo("Setting %s to %s" % (target, value))
        await dev.set_speaker_settings(target, value)

    print_settings(await dev.get_speaker_settings())


@cli.command()
@click.argument("notification", required=False)
@click.option("--listen-all", is_flag=True)
@pass_dev
@coro
async def notifications(dev: Device, notification: str, listen_all: bool):
    """List available notifications and listen to them.

    Using --listen-all [notification] allows to listen to all notifications
     from the given subsystem.
    If the subsystem is omited, notifications from all subsystems are
    requested.
    """
    notifications = await dev.get_notifications()

    async def handle_notification(x):
        click.echo("got notification: %s" % x)

    if listen_all:
        if notification is not None:
            await dev.services[notification].listen_all_notifications(
                handle_notification
            )
        else:
            click.echo("Listening to all possible notifications")
            tasks = []
            for serv in dev.services.values():
                tasks.append(
                    asyncio.ensure_future(
                        serv.listen_all_notifications(handle_notification)
                    )
                )

            await asyncio.wait(tasks)
    elif notification:
        click.echo("Subscribing to notification %s" % notification)
        for notif in notifications:
            if notif.name == notification:
                await notif.activate(handle_notification)

        click.echo("Unable to find notification %s" % notification)

    else:
        click.echo(click.style("Available notifications", bold=True))
        for notification in notifications:
            click.echo("* %s" % notification)


@cli.command()
@pass_dev
@coro
async def listen(dev: Device):
    """Listen for volume, power and content notifications."""
    from .containers import VolumeChange, PowerChange, ContentChange

    async def volume_changed(x):
        print("volume: %s" % x.volume)

    async def power_changed(x):
        print("power: %s" % x)

    async def content_changed(x):
        print("content: %s" % x)

    dev.on_notification(VolumeChange, volume_changed)
    dev.on_notification(PowerChange, power_changed)
    dev.on_notification(ContentChange, content_changed)
    await dev.listen_notifications()


@cli.command()
@pass_dev
@coro
async def sleep(dev: Device):
    """Return sleep settings."""
    click.echo(await dev.get_sleep_timer_settings())


@cli.command()
@pass_dev
def list_all(dev: Device):
    """List all available API calls."""
    for name, service in dev.services.items():
        click.echo(click.style("\nService %s" % name, bold=True))
        for method in service.methods:
            click.echo("  %s" % method.name)


@cli.command()
@click.argument("service", required=True)
@click.argument("method")
@click.argument("parameters", required=False, default=None)
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
@click.argument("file", type=click.File("w"), required=False)
@pass_dev
@coro
async def dump_devinfo(dev: Device, file):
    """Dump developer information.

    Pass `file` to write the results directly into a file.
    """
    import attr

    methods = await dev.get_supported_methods()
    res = {
        "supported_methods": {k: v.asdict() for k, v in methods.items()},
        "settings": [attr.asdict(x) for x in await dev.get_settings()],
        "sysinfo": attr.asdict(await dev.get_system_info()),
        "interface_info": attr.asdict(await dev.get_interface_information()),
    }
    if file:
        click.echo("Saving to file: %s" % file.name)
        json.dump(res, file, sort_keys=True, indent=4)
    else:
        click.echo(json.dumps(res, sort_keys=True, indent=4))


if __name__ == "__main__":
    cli()
