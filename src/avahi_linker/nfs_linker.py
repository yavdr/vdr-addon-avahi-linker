import asyncio
import logging
import os
from functools import partial
from pathlib import Path

from .config_model import ConfigModel
from .service_models import ResolvedService
from .tools import create_link, translate_path, replace_unsafe_chars

class nfsService():
    """this class holds all attributes of a detected avahi service and
    the methods to handle it"""

    def __init__(self, service: ResolvedService, config: ConfigModel):
        self.log = logging.getLogger(self.__class__.__name__)
        self.service = service
        self.config = config
        self._translate_path = partial(
            translate_path, use_i18n=self.config.options.use_i18n
        )
        self.mediadir = config.targetdirs.get('media', Path('/tmp'))
        self.vdrdir = config.targetdirs.get('vdr', Path('/tmp'))
        self.path = self.service.payload["path"]
        self.subtype = self.service.payload["subtype"]
        original = self.subtype
        self.subtype = self._translate_path(self.subtype)
        self.log.debug(f"translated {original} to {self.subtype}")
        if "category" in self.service.payload:
            self.category = self._translate_path(self.service.payload["category"])
        if self.subtype:
            self.basedir = self.mediadir / self.subtype
        else:
            raise AttributeError(
                "missing subtype for share {}\nattributes: {}".format(
                    self.service.name, self.service.payload
                )
            )
        self.update_recdir = False
        self.counter = 0
        self.job = None
        self.origin = self.get_origin()
        if not self.origin:
            return
        if self.config.options.use_hostname:
            self.sharename = (lambda host: host.split(".")[0])(self.service.host)
        else:
            self.sharename = self.service.name
        self.target = self.get_target()
        if self.subtype == "vdr":
            # sanitize name for windows clients (vdr with
            # --dirnames=,,1
            # or --fat option can display them properly)
            self.sharename = replace_unsafe_chars(self.sharename)
            # "/" is not allowed (would create a subdirectory)
            # " " would hinder the vdr to access a path
            self.sharename = self.sharename.replace("/", "-").replace(" ", "_")
            self.sharename = "".join(
                (self.config.options.nfs_prefix, self.sharename, self.config.options.nfs_suffix)
            )

            self.vdr_target = self.get_vdr_target()
            if self.vdr_target:
                self.create_link()
                self.create_extralink(self.vdr_target)
                self.update_recdir = True
        else:
            self.sharename = self.service.sharename
            self.create_link()


    def __getattr__(self, attr):
        # return None if attribute is undefined
        return self.__dict__.get(attr, None)

    def get_origin(self) -> Path:
        origin = (
            self.config.options.autofsdir
            / self.service.host.split(".")[0]
            / (self.path if not self.path.startswith(os.path.sep) else self.path[1:])
        )
        self.log.debug(
            f'called get_origin: {self.config.options.autofsdir / self.service.host.split(".")[0] / (self.path if not self.path.startswith(os.path.sep) else self.path[1:])=}'
        )
        return origin

    def get_vdr_target(self) -> Path | None:
        vdr_target = (
            self.vdrdir / (self.category if self.category is not None else "")
        ) / self.sharename
        self.log.debug(f"{vdr_target=} - {os.path.abspath(vdr_target)=}")
        if os.path.commonprefix([vdr_target, self.vdrdir]).startswith(
            str(self.vdrdir)
        ):
            # if os.path.abspath(vdr_target).startswith(str(self.config.vdrdir)):
            return vdr_target
        else:
            self.log.error("Path %s is outside of vdrdir - ignoring" % vdr_target)
            return None

    def get_target(self) -> Path:
        category = (lambda category: category if category is not None else "")(
            self.category
        )
        target = self.basedir / category / self.sharename
        if os.path.abspath(target).startswith(str(self.basedir)):
            return target
        else:
            self.log.error("Path {target} is outside of basedir - ignoring")
            raise ValueError("Path {target} is outside of basedir")

    def create_link(self):
        if (
            self.target
            and not os.path.islink(self.target)
            and not os.path.exists(self.target)
        ):
            self.target.parent.mkdir(parents=True, exist_ok=True)
            if self.subtype == "vdr":
                self.target = Path(f"{self.target} for {self.config.options.hostname}")
            elif self.config.options.use_hostname:
                self.target = self.target
            try:
                create_link(self.origin, Path(self.target))
                self.log.debug(
                    f"created symlink from {self.origin} to {self.target} for {self.sharename}"
                )
            except Exception as err:
                self.log.exception("could not create symlink")
                self.log.debug(
                    "symlink from '{}' to '{}' for '{}' already exists".format(
                        self.origin, self.target, self.sharename
                    )
                )

    def create_extralink(self, target: Path):
        if self.target and target and not os.path.islink(target) and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            # self.mkdir_p(os.path.dirname(target))
            os.symlink(Path(self.target), target)
            self.log.debug("created additional symlink for remote VDR dir")

    async def wait_for_path(self, path: Path):
        timeout = 0
        while True:
            if self.origin.exists():
                self.log.debug("autofs-path exists: %s" % (self.origin))
                return True
            self.log.debug("autofs-path does not exist, try again in 1s")
            await asyncio.sleep(1)
            timeout += 1
            if timeout > 120:
                self.log.debug("autofs-path was not available within 120s, giving up")
                return False

    def unlink(self):
        self.log.debug(f"avahi-share: unlinking {self.target=}")
        if self.target is not None:
            self.target.unlink(missing_ok=True)
        self.log.debug(f"avahi-share: unlinking {self.vdr_target=}")
        if self.vdr_target and self.subtype == "vdr":
            self.vdr_target.unlink(missing_ok=True)
            self.update_recdir = True