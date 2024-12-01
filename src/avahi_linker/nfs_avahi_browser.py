import asyncio
import logging
import avahi
from pydantic import ValidationError
from avahi_linker.avahi_interface import (
    OrgFreedesktopAvahiServerInterface,
    OrgFreedesktopAvahiServiceBrowserInterface,
)
from .config_model import ConfigModel
from .nfs_linker import nfsService
from .service_models import AvahiAnnouncement
from .tools import SYSTEM_BUS, ip_is_whitelisted, resolve_avahi_announcement


class NFSAvahiBrowser:
    NFS_TYPE = "_nfs._tcp"
    DOMAIN = "local"
    FLAGS = 0

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        config: ConfigModel,
        update_requests: asyncio.Queue,
    ):
        self.log = logging.getLogger(self.__class__.__name__)
        self.loop = loop
        self.linked_services: dict[str, nfsService] = {}
        self.config = config
        self.update_requests = update_requests

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        for service_name, service in self.linked_services.items():
            self.log.debug(f"removing links for {service_name}")
            service.unlink()

    async def avahi_browser(self) -> tuple[asyncio.Task, asyncio.Task]:
        service = OrgFreedesktopAvahiServerInterface.new_proxy(
            avahi.DBUS_NAME, "/", bus=SYSTEM_BUS
        )
        browser_addr = await service.service_browser_new(
            avahi.IF_UNSPEC, avahi.PROTO_UNSPEC, self.NFS_TYPE, self.DOMAIN, self.FLAGS
        )
        browser = OrgFreedesktopAvahiServiceBrowserInterface.new_proxy(
            avahi.DBUS_INTERFACE_SERVICE_BROWSER, browser_addr, bus=SYSTEM_BUS
        )

        async def handle_new_items():
            # try:
            async for item in browser.item_new:
                item = AvahiAnnouncement(*item)
                if item.is_local():
                    continue

                try:
                    avahi_data = await resolve_avahi_announcement(item, service)
                except ValidationError:
                    self.log.exception("invalid service properties, skipping")
                    continue

                if (
                    ip_is_whitelisted(self.config.options, avahi_data.address)
                    and avahi_data.extended_sharename not in self.linked_services
                ):
                    self.log.debug(
                        f"avahi service resolved: {avahi_data.extended_sharename}"
                    )
                    try:
                        share = nfsService(avahi_data, self.config)
                    except Exception:
                        self.log.exception("could not link nfsService")
                    else:
                        self.linked_services[avahi_data.extended_sharename] = share
                        if share.update_recdir:
                            await self.update_requests.put(True)
                            share.update_recdir = False
            # except asyncio.CancelledError:
            #     return

        async def handle_removed_items():
            # try:
            async for item in browser.item_remove:
                item = AvahiAnnouncement(*item)
                if item.is_local():
                    continue
                try:
                    sharename, share = next(
                        (
                            (sharename, share)
                            for sharename, share in self.linked_services.items()
                            if share.name == item.name
                        )
                    )
                except StopIteration:
                    self.log.debug(f"no share found for name {item.name}")
                    continue
                self.log.debug(f"removing {sharename} ({share})")
                if s := self.linked_services.pop(sharename, None):
                    s.unlink()
                    if s.update_recdir:
                        await self.update_requests.put(True)
                        s.update_recdir = False

                self.log.debug(f"processed {item=}")
            # except asyncio.CancelledError:
            #     return

        return asyncio.create_task(
            handle_new_items(), name="on_new_item"
        ), asyncio.create_task(handle_removed_items(), name="on_removed_item")
