from __future__ import annotations

from typing import List, Tuple

from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_signal_async,
)


class OrgFreedesktopAvahiServerInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.Avahi.Server",
):
    @dbus_method_async(
        result_signature="s",
    )
    async def get_version_string(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="u",
    )
    async def get_apiversion(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
    )
    async def get_host_name(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
    )
    async def set_host_name(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
    )
    async def get_host_name_fqdn(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
    )
    async def get_domain_name(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="b",
    )
    async def is_nsssupport_available(
        self,
    ) -> bool:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="i",
    )
    async def get_state(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="u",
    )
    async def get_local_service_cookie(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="s",
    )
    async def get_alternative_host_name(
        self,
        name: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="s",
    )
    async def get_alternative_service_name(
        self,
        name: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="i",
        result_signature="s",
    )
    async def get_network_interface_name_by_index(
        self,
        index: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="i",
    )
    async def get_network_interface_index_by_name(
        self,
        name: str,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisiu",
        result_signature="iisisu",
    )
    async def resolve_host_name(
        self,
        interface: int,
        protocol: int,
        name: str,
        aprotocol: int,
        flags: int,
    ) -> Tuple[int, int, str, int, str, int]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisu",
        result_signature="iiissu",
    )
    async def resolve_address(
        self,
        interface: int,
        protocol: int,
        address: str,
        flags: int,
    ) -> Tuple[int, int, int, str, str, int]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisssiu",
        result_signature="iissssisqaayu",
    )
    async def resolve_service(
        self,
        interface: int,
        protocol: int,
        name: str,
        type: str,
        domain: str,
        aprotocol: int,
        flags: int,
    ) -> Tuple[int, int, str, str, str, str, int, str, int, List[bytes], int]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="o",
    )
    async def entry_group_new(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisiu",
        result_signature="o",
    )
    async def domain_browser_new(
        self,
        interface: int,
        protocol: int,
        domain: str,
        btype: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisu",
        result_signature="o",
    )
    async def service_type_browser_new(
        self,
        interface: int,
        protocol: int,
        domain: str,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iissu",
        result_signature="o",
    )
    async def service_browser_new(
        self,
        interface: int,
        protocol: int,
        type: str,
        domain: str,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisssiu",
        result_signature="o",
    )
    async def service_resolver_new(
        self,
        interface: int,
        protocol: int,
        name: str,
        type: str,
        domain: str,
        aprotocol: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisiu",
        result_signature="o",
    )
    async def host_name_resolver_new(
        self,
        interface: int,
        protocol: int,
        name: str,
        aprotocol: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisu",
        result_signature="o",
    )
    async def address_resolver_new(
        self,
        interface: int,
        protocol: int,
        address: str,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisqqu",
        result_signature="o",
    )
    async def record_browser_new(
        self,
        interface: int,
        protocol: int,
        name: str,
        clazz: int,
        type: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="is",
    )
    def state_changed(self) -> Tuple[int, str]:
        raise NotImplementedError


class OrgFreedesktopAvahiServer2Interface(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.Avahi.Server2",
):
    @dbus_method_async(
        result_signature="s",
    )
    async def get_version_string(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="u",
    )
    async def get_apiversion(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
    )
    async def get_host_name(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
    )
    async def set_host_name(
        self,
        name: str,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
    )
    async def get_host_name_fqdn(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
    )
    async def get_domain_name(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="b",
    )
    async def is_nsssupport_available(
        self,
    ) -> bool:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="i",
    )
    async def get_state(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="u",
    )
    async def get_local_service_cookie(
        self,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="s",
    )
    async def get_alternative_host_name(
        self,
        name: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="s",
    )
    async def get_alternative_service_name(
        self,
        name: str,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="i",
        result_signature="s",
    )
    async def get_network_interface_name_by_index(
        self,
        index: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="i",
    )
    async def get_network_interface_index_by_name(
        self,
        name: str,
    ) -> int:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisiu",
        result_signature="iisisu",
    )
    async def resolve_host_name(
        self,
        interface: int,
        protocol: int,
        name: str,
        aprotocol: int,
        flags: int,
    ) -> Tuple[int, int, str, int, str, int]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisu",
        result_signature="iiissu",
    )
    async def resolve_address(
        self,
        interface: int,
        protocol: int,
        address: str,
        flags: int,
    ) -> Tuple[int, int, int, str, str, int]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisssiu",
        result_signature="iissssisqaayu",
    )
    async def resolve_service(
        self,
        interface: int,
        protocol: int,
        name: str,
        type: str,
        domain: str,
        aprotocol: int,
        flags: int,
    ) -> Tuple[int, int, str, str, str, str, int, str, int, List[bytes], int]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="o",
    )
    async def entry_group_new(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisiu",
        result_signature="o",
    )
    async def domain_browser_prepare(
        self,
        interface: int,
        protocol: int,
        domain: str,
        btype: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisu",
        result_signature="o",
    )
    async def service_type_browser_prepare(
        self,
        interface: int,
        protocol: int,
        domain: str,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iissu",
        result_signature="o",
    )
    async def service_browser_prepare(
        self,
        interface: int,
        protocol: int,
        type: str,
        domain: str,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisssiu",
        result_signature="o",
    )
    async def service_resolver_prepare(
        self,
        interface: int,
        protocol: int,
        name: str,
        type: str,
        domain: str,
        aprotocol: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisiu",
        result_signature="o",
    )
    async def host_name_resolver_prepare(
        self,
        interface: int,
        protocol: int,
        name: str,
        aprotocol: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisu",
        result_signature="o",
    )
    async def address_resolver_prepare(
        self,
        interface: int,
        protocol: int,
        address: str,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="iisqqu",
        result_signature="o",
    )
    async def record_browser_prepare(
        self,
        interface: int,
        protocol: int,
        name: str,
        clazz: int,
        type: int,
        flags: int,
    ) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="is",
    )
    def state_changed(self) -> Tuple[int, str]:
        raise NotImplementedError


class OrgFreedesktopAvahiServiceBrowserInterface(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.Avahi.ServiceBrowser",
):
    @dbus_method_async(
    )
    async def free(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
    )
    async def start(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="iisssu",
    )
    def item_new(self) -> Tuple[int, int, str, str, str, int]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="iisssu",
    )
    def item_remove(self) -> Tuple[int, int, str, str, str, int]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="s",
    )
    def failure(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
    )
    def all_for_now(self) -> None:
        raise NotImplementedError

    @dbus_signal_async(
    )
    def cache_exhausted(self) -> None:
        raise NotImplementedError