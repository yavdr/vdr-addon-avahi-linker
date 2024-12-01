import argparse
import logging
import sys
from configparser import ConfigParser
from pathlib import Path

from .config_model import ConfigModel, LoggingOptions


def set_up_logger(options: LoggingOptions) -> None:
    if options.use_file:
        logging.basicConfig(
            filename=options.logfile,
            level=getattr(logging, options.loglevel),
            # format="%(asctime)-15s %(levelname)-6s %(message)s",
        )
    else:
        logging.basicConfig(
            level=getattr(logging, options.loglevel),
            # format="%(asctime)-15s %(levelname)-6s %(message)s",
        )


def read_config_files(configfile: Path) -> ConfigModel:
    """read all config files for avahi-linker from configdir.
    DO NOT USE logging calls until logging is set up!"""
    log = logging.getLogger("read_config_files")
    parser = ConfigParser()
    try:
        parser.read(configfile)
    except OSError as e:
        log.exception(f"could not read config file {configfile}: {e.strerror}")
        sys.exit(f"could not read config file {configfile}")
    configdir = configfile.parent
    for opt_config in (
        "staticmount.cfg",
        "localdirs.cfg",
        "wfe-static.cfg",
    ):
        try:
            parser.read(configdir / opt_config)
        except OSError as _:
            pass
        except Exception as e:
            print(e, file=sys.stderr)
        else:
            print(f"read config file {opt_config}")
    return ConfigModel(**parser)


def get_config_file() -> Path:
    argparser = argparse.ArgumentParser(description="link avahi announced nfs shares")
    argparser.add_argument(
        "-c",
        "--config",
        dest="config",
        action="store",
        help="config file(s)",
        default="/etc/avahi-linker/default.cfg",
        metavar="CONFIG_FILE",
    )

    return Path(argparser.parse_args().config)


def read_config() -> ConfigModel:
    configfile = get_config_file()
    config = read_config_files(configfile)
    set_up_logger(config.Logging)
    return config
