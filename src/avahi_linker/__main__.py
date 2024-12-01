import asyncio
import gettext
import logging
import signal
import sys
from functools import partial

from .config import read_config
from .nfs_avahi_browser import NFSAvahiBrowser
from .config_model import ConfigModel
from .local_linker import LocalLinker
from .tools import update_recordings_async, update_recordings_sync
from .vdr_dbus_interface import get_status_interface
from . import vdr_net_monitor
from . import prevent_unmount_on_pause

update_requests = asyncio.Queue()


async def process_update_recording_requests(config: ConfigModel) -> None:
    # try:
    while True:
        update = False
        while not update_requests.empty():
            _ = await update_requests.get()
            update = True
        if update:
            await update_recordings_async(config)
        await asyncio.sleep(1)
    # except asyncio.CancelledError:
    #     return


def on_shutdown(signal: signal.Signals, tasks: tuple[asyncio.Task, ...]) -> None:
    logging.debug(f"received {signal=}, shutting down...")
    for t in tasks:
        logging.debug(f"canceling task: {t}")
        t.cancel()


def setup_signal_handler(
    tasks: tuple[asyncio.Task, ...], loop: asyncio.AbstractEventLoop
) -> None:
    cb = partial(on_shutdown, tasks=tasks)

    for sig in (signal.SIGHUP, signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, cb, sig)


def main():
    config = read_config()
    gettext.install("avahi-linker")  # , "/usr/share/locale")
    # print(config.options)
    loop = asyncio.new_event_loop()
    with (
        NFSAvahiBrowser(
            loop=loop, config=config, update_requests=update_requests
        ) as avahi_browser,
        LocalLinker(config=config, update_requests=update_requests) as _local_linker,
    ):

        async def handle_asnyc_stuff(avahi_browser: NFSAvahiBrowser):
            handle_new, handle_removed = await avahi_browser.avahi_browser()
            update_recordings_t = asyncio.create_task(
                process_update_recording_requests(config), name="update_recordings"
            )
            net_monitor_t = asyncio.create_task(
                vdr_net_monitor.main(), name="handle update requests"
            )
            prevent_unmount_on_pause_t = asyncio.create_task(
                prevent_unmount_on_pause.watch_replay_status(
                    get_status_interface(config.options.vdr_instance_id)
                ),
                name="prevent umount on pause",
            )
            tasks = (
                handle_new,
                handle_removed,
                update_recordings_t,
                net_monitor_t,
                prevent_unmount_on_pause_t,
            )
            setup_signal_handler(tasks=tasks, loop=loop)
            return_values = await asyncio.gather(*tasks, return_exceptions=True)
            for r in return_values:
                if not isinstance(r, asyncio.CancelledError):
                    logging.debug(f"{r!r}")

        try:
            loop.run_until_complete(handle_asnyc_stuff(avahi_browser=avahi_browser))
        except KeyboardInterrupt:
            sys.exit(
                130
            )  # make the KeyboardInterrupt a proper signal, so the cleanup works
        finally:
            loop.close()
    logging.info("update recordings")
    update_recordings_sync(config=config)


if __name__ == "__main__":
    main()
