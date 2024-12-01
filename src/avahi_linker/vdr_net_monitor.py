import asyncio
from contextlib import closing
import ipaddress
import logging
from pathlib import Path
import socket
import re
import aionotify
import sdbus
import sdbus.exceptions

from .config import read_config
from .config_model import ConfigModel
from .tools import update_recordings_async
from .vdr_dbus_interface import (
    Recording,
    get_recording_interface,
)

UPDATE_LOCK = asyncio.Lock()

log = logging.getLogger("VDR Net Monitor")


class UdpServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, config: ConfigModel):
        self.log = logging.getLogger("UdpServerProtocol")
        self.config = config
        self.hostname = socket.gethostname()
        self.hostname_re = re.compile(r"\w+_on_(?P<hostname>\w+)")

    def connection_made(self, transport):
        self.log.debug("connection established")
        self.transport = transport

    def datagram_received(self, data, addr):
        if not self.config.options.receive_udp_notifications:
            return
        origin = ipaddress.ip_address(addr[0])
        self.log.debug(f"got datagram: {data} from {addr}")
        if origin.is_loopback:
            self.log.debug("ignoring message from local loopback address")
            return
        try:
            remote_hostname, _, message = data.decode("utf-8").partition(":")
        except UnicodeDecodeError:
            self.log.exception("could not decode message")
            return

        message = message.rstrip()

        if remote_hostname != self.hostname and message == "update":
            self.log.info("received request to update recordings")
            t = asyncio.create_task(update_recordings_async(self.config))
            _ = asyncio.gather(t)
        elif remote_hostname == self.hostname and message.startswith("cut;"):
            cmd, _, path = message.partition(";")
            if m := self.hostname_re.search(path):
                host_with_recording = m.group("hostname")
                if host_with_recording == self.hostname:
                    p = Path(path)
                    self.log.debug("looking for recording: {path}")

        async def lookup_recording_by_path(path: Path):
            try:
                vdr_recordings = get_recording_interface(
                    self.config.options.vdr_instance_id
                )
                recordings = Recording.from_DBusData(await vdr_recordings.list())

            except sdbus.exceptions.DbusFailedError as e:
                self.log.exception(f"could not list recordings using dbus2vdr plugin")

    def error_received(self, exc):
        self.log.error(exc)


async def watch_update_file(config: ConfigModel, transport: asyncio.DatagramTransport):
    hostname = socket.gethostname()
    if config.options.watch_update_file:
        watcher = aionotify.Watcher()
        watcher.watch(
            alias=".update",
            path=str(config.options.vdr_rec_dir),
            flags=aionotify.Flags.ATTRIB,
        )
        loop = asyncio.get_event_loop()
        await watcher.setup(loop)
        log.info(f"watching {config.options.vdr_rec_dir}")
        while True:
            event = await watcher.get_event()
            if event and event.name == ".update":
                log.debug(f"watcher got {event}")
                if config.options.send_udp_notifications:
                    log.info("send update notification as udp broadcast")
                    transport.sendto(
                        f"{hostname}:update".encode("utf-8"),
                        ("255.255.255.255", config.options.udp_port),
                    )
    else:
        await asyncio.Future()  # this waits forever, so the receiver part will still work


async def main():
    config = read_config()
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UdpServerProtocol(config),
        local_addr=("0.0.0.0", config.options.udp_port),
        allow_broadcast=True,
        reuse_port=True,
    )

    with closing(transport) as t:
        _ = await asyncio.gather(watch_update_file(config, transport))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
