from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class HotkeyInfo(VTSBaseModel):
    name: str
    type: str
    description: str
    file: str
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    key_combination: list[str]
    on_screen_button_id: Annotated[int, Field(alias="onScreenButtonID")]


class HotkeysInCurrentModelRequest(VTSBaseModel):
    model_id: Annotated[str | None, Field(alias="modelID")] = None
    live2d_item_file_name: Annotated[
        str | None,
        Field(alias="live2DItemFileName"),
    ] = None


class HotkeysInCurrentModelResponse(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    available_hotkeys: list[HotkeyInfo]


class HotkeyTriggerRequest(VTSBaseModel):
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    item_instance_id: Annotated[str | None, Field(alias="itemInstanceID")] = None


class HotkeyTriggerResponse(VTSBaseModel):
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
