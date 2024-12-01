from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Extra, Field
from sdbus import (
    DbusInterfaceCommonAsync,
    dbus_method_async,
    dbus_signal_async,
)
import sdbus

SYSTEM_BUS = sdbus.sd_bus_open_system()


def get_vdr_dbus_address(vdr_instance_id: int = 0):
    return f"de.tvdr.vdr{'' if vdr_instance_id == 0 else {vdr_instance_id}}"


class DeTvdrVdrRecordingInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.recording",
):
    @dbus_method_async(
        result_signature="is",
    )
    async def update(
        self,
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="v",
        result_signature="(ia(sv))",
    )
    async def get(
        self,
        number_or_path: Tuple[str, Any],
    ) -> Tuple[int, List[Tuple[str, Tuple[str, Any]]]]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="a(ia(sv))",
    )
    async def list(
        self,
    ) -> List[Tuple[int, List[Tuple[str, Tuple[str, Any]]]]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="vv",
        result_signature="is",
    )
    async def play(
        self,
        number_or_path: Tuple[str, Any],
        begin: Tuple[str, Any],
    ) -> Tuple[int, str]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="vs",
        result_signature="is",
    )
    async def change_name(
        self,
        number_or_path: Tuple[str, Any],
        newname: str,
    ) -> Tuple[int, str]:
        raise NotImplementedError


def get_recording_interface(vdr_instance_id: int = 0):
    return DeTvdrVdrRecordingInterface.new_proxy(
        get_vdr_dbus_address(vdr_instance_id), "/Recordings", SYSTEM_BUS
    )


class DeTvdrVdrStatusInterface(
    DbusInterfaceCommonAsync,
    interface_name="de.tvdr.vdr.status",
):
    @dbus_method_async(
        result_signature="ssb",
    )
    async def is_replaying(
        self,
    ) -> Tuple[str, str, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="s",
    )
    def channel_change(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ss",
    )
    def timer_change(self) -> Tuple[str, str]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="iib",
    )
    def channel_switch(self) -> Tuple[int, int, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="issb",
    )
    def recording(self) -> Tuple[int, str, str, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ssb",
    )
    def replaying(self) -> Tuple[str, str, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ib",
    )
    def set_volume(self) -> Tuple[int, bool]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ias",
    )
    def set_audio_track(self) -> Tuple[int, List[str]]:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="i",
    )
    def set_audio_channel(self) -> int:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="ias",
    )
    def set_subtitle_track(self) -> Tuple[int, List[str]]:
        raise NotImplementedError


def get_status_interface(vdr_instance_id: int = 0):
    return DeTvdrVdrStatusInterface.new_proxy(
        get_vdr_dbus_address(vdr_instance_id), "/Status", SYSTEM_BUS
    )

RawRecordingList = List[Tuple[int, List[Tuple[str, Tuple[str, Any]]]]]


class RecComponent(BaseModel):
    stream: int
    type: int
    language: str


class RecInfo(BaseModel):
    channel_id: str = Field(alias="ChannelID", default="")
    channel_name: str = Field(alias="ChannelName", default="")
    title: str = Field(alias="Title", default="")
    short_text: str = Field(alias="ShortText", default="")
    description: str = Field(alias="Description", default="")
    fps: float = Field(alias="FramesPerSecond", default=-1)
    component: dict[int, RecComponent] = Field(alias="Component")


class Recording(BaseModel):
    rec_id: int
    path: Path = Field(alias="Path")
    name: str = Field(alias="Name")
    full_name: str = Field(alias="FullName")
    title: str = Field(alias="Title")
    start: int = Field(alias="Start")
    priority: int = Field(alias="Priority")
    lifetime: int = Field(alias="Lifetime")
    hierarchy_levels: int = Field(alias="HierarchyLevels")
    fps: float = Field(alias="FramesPerSecond")
    num_frames: int = Field(alias="NumFrames")
    length_in_seconds: int = Field(alias="LengthInSeconds")
    file_size_mb: int = Field(alias="FileSizeMB")
    is_pes_recording: bool = Field(alias="IsPesRecording")
    is_new: bool = Field(alias="IsNew")
    is_edited: bool = Field(alias="IsEdited")
    Info: RecInfo

    @classmethod
    def from_DBusData(
        cls, raw_data: RawRecordingList
    ) -> list["Recording"]:
        recordings: list[Recording] = []
        for r in raw_data:
            streams: dict[int, dict[str, str]] = {}
            rec_data: dict[str, Any] = {"Info": {"Component": defaultdict(dict)}}
            rec_id, rec_raw_data = r
            rec_data["rec_id"] = rec_id

            for k, v in rec_raw_data:
                _, v = v
                k, sep, rest = k.partition("/")
                if sep == "/":
                    match rest.split("/"):
                        case [nested_key]:
                            rec_data[k][nested_key] = v
                        case [nested_key, num_stream, stream_key]:
                            rec_data[k][nested_key][int(num_stream)][stream_key] = v
                else:
                    rec_data[k] = v

            rec = Recording(**rec_data)
            recordings.append(rec)

        return recordings
