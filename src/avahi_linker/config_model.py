import ipaddress
import socket
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, IPvAnyNetwork, DirectoryPath, FilePath, validator

# from tools import replace_unsafe_chars

UNSAFE_CHARS = ("<", ">", "?", "&", '"', ":", "|", "\\", "*")


def replace_unsafe_chars(string: str) -> str:
    for char in UNSAFE_CHARS:
        string = string.replace(char, "#{0:x}".format(ord(char)))
    return string


class Options(BaseModel):
    fat_safe_names: bool = Field(default=True)
    dbus2vdr: bool = Field(default=False)
    vdr_instance_id: int = Field(default=0)
    vdr_rec_dir: FilePath = Field(default=Path("/srv/vdr/video"))
    svdr_port: int = Field(default=6419)
    udp_port: int = Field(default=5555)
    send_udp_notifications: bool = Field(default=True)
    receive_udp_notifications: bool = Field(default=True)
    watch_update_file: bool = Field(default=True)
    autofsdir: DirectoryPath = Field(default=Path("/net"))
    use_i18n: bool = Field(default=True)
    nfs_prefix: str = Field(default="")
    nfs_suffix: str = Field(default="(nfs)")
    static_suffix: str = Field(default="[static]")
    ip_whitelist: list[IPvAnyNetwork] = Field(
        default_factory=lambda: list(
            (ipaddress.ip_network("0.0.0.0/0"), ipaddress.ip_network("0::0/0"))
        )
    )
    ip_blacklist: list[IPvAnyNetwork] = Field(default_factory=list)
    hostname: str = Field(default_factory=socket.gethostname)
    vdr_user: str = Field(default="vdr")
    vdr_group: str = Field(default="vdr")
    use_hostname: bool = Field(default=False)

    @validator("ip_whitelist", "ip_blacklist", pre=True)
    def split_str(cls, v):
        return v.split(" ")

    @validator(
        "nfs_prefix", "nfs-suffix", "static_suffix", always=True, check_fields=False
    )
    def guard_replace_unsafe_chars(cls, value: str, values: dict[str, Any]) -> str:
        if values["fat_safe_names"]:
            return replace_unsafe_chars(value)
        else:
            return value


class LOGLEVEL(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggingOptions(BaseModel):
    use_file: bool = Field(default=False)
    logfile: Path = Field(default=Path("/tmp/avahi-linker.log"))
    loglevel: LOGLEVEL = Field(default=LOGLEVEL.INFO)


class ConfigModel(BaseModel):
    localdirs: dict[str, Path]
    media_static_mount: dict[str, Path]
    vdr_static_mount: dict[str, Path]
    targetdirs: dict[str, Path] = Field(
        default_factory=lambda: {
            "media": "/media",
            "vdr": "/srv/vdr/video",
        }
    )
    options: Options
    Logging: LoggingOptions
