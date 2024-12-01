import asyncio
import logging
from functools import partial
from pathlib import Path

from avahi_linker.config import ConfigModel
from avahi_linker.tools import create_link, translate_path, unlink, update_recordings_async


class LocalLinker:
    def __init__(self, config: ConfigModel, update_requests: asyncio.Queue) -> None:
        self.log = logging.getLogger(self.__class__.__name__)
        self.update_request = update_requests
        self.created_links: list[Path] = []
        self.config = config
        self.mediadir = self.config.targetdirs.get("media", Path("/tmp"))
        self.vdrdir = self.config.targetdirs.get("vdr", Path("/tmp"))
        self._translate_path = partial(
            translate_path, use_i18n=self.config.options.use_i18n
        )
        for subtype, localdir in config.localdirs.items():
            subtype = self._translate_path(subtype)
            if create_link(localdir, link_path := self.mediadir / subtype / "local"):
                self.created_links.append(link_path)

        for subtype, netdir in config.media_static_mount.items():
            subtype, localdir, host = self.prepare(subtype, netdir)
            if create_link(
                localdir,
                link_path := self.mediadir
                / (subtype + self.config.options.static_suffix),
            ):
                self.created_links.append(link_path)

        for subtype, netdir in config.vdr_static_mount.items():
            subtype, localdir, host = self.prepare(subtype, netdir)
            self.log.debug("static vdr dir: %s" % netdir)
            self.log.debug("path is '%s'" % subtype)
            basedir = self.mediadir / subtype
            target = self.get_target("vdr", subtype, host)
            vdr_target = self.get_vdr_target(subtype, host)
            create_link(localdir, target)
            self.created_links.append(target)
            create_link(target, vdr_target)
            self.created_links.append(vdr_target)
            self.update_request.put_nowait(True)

    def __enter__(self) -> "LocalLinker":
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback) -> None:
        self.unlink_all()

    def prepare(self, subtype: str, netdir: Path):
        subtype = self._translate_path(subtype)
        self.log.debug(f"{subtype=}, {self.config.options.autofsdir=}, {netdir=}")
        localdir = self.config.options.autofsdir / netdir
        host = netdir.parts[0]
        self.log.debug("Host: {0} type {1}".format(host, type(host)))
        return subtype, localdir, host

    def get_target(self, vdr: str, subtype: str, host: str) -> Path:
        return (
            self.mediadir
            / vdr
            / subtype
            / (host + f"(for static {self.config.options.hostname})")
        )

    def get_vdr_target(self, subtype, host):
        target = self.vdrdir / (subtype + self.config.options.static_suffix)
        self.log.debug(f"vdr target: {target}")
        return target

    def unlink_all(self):
        for l in self.created_links:
            try:
                self.log.debug(f"removing link {l}")
                l.unlink(missing_ok=True)
            except IOError as err:
                self.log.exception(f"Could not unlink {l}")
        else:
            self.update_request.put_nowait(True)
