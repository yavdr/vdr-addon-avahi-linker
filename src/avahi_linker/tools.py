import avahi
import gettext
import logging
import os
from pathlib import Path
import shutil
from pydantic import IPvAnyAddress
import sdbus
from avahi_linker.avahi_interface import OrgFreedesktopAvahiServerInterface
from avahi_linker.config_model import ConfigModel, Options, replace_unsafe_chars
from avahi_linker.service_models import AvahiAnnouncement, ResolvedService
from avahi_linker.vdr_dbus_interface import DeTvdrVdrRecordingInterface, Recording
from avahi_linker.svdrp import send_svdrpcommand, SVDRP

replace_unsafe_chars = replace_unsafe_chars

gettext.install("avahi-linker")
SYSTEM_BUS = sdbus.sd_bus_open_system()


def translate_path(path: str, use_i18n=False):
    elsub = []
    path = path.lstrip(os.path.sep)  # remove leading path separator
    if use_i18n:
        for element in path.split("/"):
            elsub.append(_("%s" % element)) # type: ignore
        path = "/".join(elsub)
    return path


def create_link(origin: Path, target: Path) -> bool:
    log = logging.getLogger("tools:create_link")
    # exists on a dead symlink returns false
    # so we need to check if it is a symlink, too
    # if not target.exists() and not target.is_symlink():
    if not os.path.exists(target) and not os.path.islink(target):
        try:
            # target.parent.mkdir(exist_ok=True, parents=True)
            target.parent.mkdir(exist_ok=True, parents=True)
            log.debug("created directory {}".format(target))
        except OSError as e:
            log.error(e)
            return False
        try:
            # target.symlink_to(origin)
            os.symlink(origin, target)
            log.debug("created symlink from {} to {}".format(target, origin))
        except FileExistsError:
            return True
        except OSError as e:
            log.error(e)
            return False
    return True


def unlink(target: Path | str):
    if os.path.exists(
        target
    ):  # and os.path.islink(target):  # a dead symlink would not be removed if we check if target is a link
        logging.debug(f"remove link {target}")
        try:
            os.unlink(target)  # target.unlink(missing_ok=True)
        except OSError as e:
            logging.error(e)


async def update_recordings_async(
    config: ConfigModel, vdr_rec_dir: Path = Path("/srv/vdr/video")
):
    try:
        if config.options.dbus2vdr:
            vdr = DeTvdrVdrRecordingInterface.new_proxy(
                "de.tvdr.vdr", "/Recordings", bus=SYSTEM_BUS
            )
            await vdr.update()
        else:
            async with SVDRP(port=config.options.svdr_port) as svdrp:
                try:
                    await svdrp.send_cmd("UPDR")
                except Exception:
                    logging.exception("could not update recordings, vdr not running")
            # await send_svdrpcommand("UPDR")
    except Exception as e:
        logging.exception(
            f"could not connect to vdr using {'dbus2vdr' if config.options.dbus2vdr else 'svdrp'}"
        )

def update_recordings_sync(config: ConfigModel):
    try:
        update_file = config.options.vdr_rec_dir / ".update"
        # update_file = vdr_rec_dir / ".update"
        update_file.touch(exist_ok=True)
        shutil.chown(update_file, config.options.vdr_user, config.options.vdr_group)
    except Exception as e:
        logging.exception(f"could not touch .update file")


async def resolve_avahi_announcement(
    item: AvahiAnnouncement, service: OrgFreedesktopAvahiServerInterface
) -> ResolvedService:
    data = await service.resolve_service(
        item.interface,
        item.protocol,
        item.name,
        item.service_type,
        item.domain,
        avahi.PROTO_UNSPEC,
        0,
    )
    return ResolvedService(
        **{k: v for k, v in zip(ResolvedService.__fields__.keys(), data)}
    )


def ip_is_whitelisted(options: Options, address: IPvAnyAddress):
    return any(
        ip_range for ip_range in options.ip_whitelist if address in ip_range
    ) and not any(ip_range for ip_range in options.ip_blacklist if address in ip_range)


def best_recording_match(
    path: Path, recording_list: list[Recording]
) -> Recording | None:
    parts = list(reversed(path.parts))
    best_match = (0, None)
    for r in recording_list:
        r_parts = list(reversed(r.path.parts))
        # print(f"{r_parts=}")
        n_matches = 0
        for local, remote in zip(parts, r_parts):
            if local == remote:
                # print(f"match: {local}")
                n_matches += 1
            else:
                break
        if n_matches >= 2:
            if n_matches > best_match[0]:
                best_match = (n_matches, r)
    return best_match[1]
