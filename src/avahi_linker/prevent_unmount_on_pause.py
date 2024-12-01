import asyncio
import logging
import sys
from pathlib import Path
from typing import IO

from .config import read_config
from .vdr_dbus_interface import get_status_interface, DeTvdrVdrStatusInterface


async def watch_replay_status(vdr_status: DeTvdrVdrStatusInterface):
    # This function reacts on "Replaying" dbus messages of the dbus2vdr plugin for VDR.
    # If a recording on a different filesystem than the VDRDIR's filesystem is played,
    # the index file of this recording is opened until replay has been stopped.
    # This prevents unwanted umounts by autofs inacitivty timeouts, if the replay
    # is paused too long.
    log = logging.getLogger("VDR Replay Status Watcher")
    current_recording: IO | None = None
    try:
        async for name, path, status in vdr_status.replaying:
            log.debug(f"{name=}, {path=}, {status=}")
            if not status and current_recording:
                log.debug(f"closing {current_recording.name}")
                current_recording.close()
                current_recording = None
            if status:
                index_path = Path(path) / 'index'
                if not index_path.exists():
                    index_path = Path(path) / 'index.vdr'
                if not index_path.exists():
                    logging.debug(f"no index file found for {path}, skipping this replay")
                    continue
                log.debug(f"opening {index_path}")
                try:
                    current_recording = open(index_path, "r")
                except Exception as err:
                    log.exception(err)
    finally:
        if current_recording:
            current_recording.close()

def main():
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    config = read_config()
    vdr_status = get_status_interface(config.options.vdr_instance_id)
    sys.exit(asyncio.run(watch_replay_status(vdr_status)))


if __name__ == "__main__":
    main()
