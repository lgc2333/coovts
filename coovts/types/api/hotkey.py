from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..registry import request_model, response_model, response_param_model


@response_param_model
class HotkeyInfo(BaseModel):
    name: str
    type: str
    description: str
    file: str
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    key_combination: list[str]
    on_screen_button_id: Annotated[int, Field(alias="onScreenButtonID")]


@request_model
class HotkeysInCurrentModelRequest(BaseModel):
    msg_t: ClassVar[str] = "HotkeysInCurrentModelRequest"
    model_id: Annotated[str | None, Field(alias="modelID")] = None
    live2d_item_file_name: Annotated[
        str | None,
        Field(alias="live2DItemFileName"),
    ] = None


@response_model
class HotkeysInCurrentModelResponse(BaseModel):
    msg_t: ClassVar[str] = "HotkeysInCurrentModelResponse"
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    available_hotkeys: list[HotkeyInfo]


@request_model
class HotkeyTriggerRequest(BaseModel):
    msg_t: ClassVar[str] = "HotkeyTriggerRequest"
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    item_instance_id: Annotated[str | None, Field(alias="itemInstanceID")] = None


@response_model
class HotkeyTriggerResponse(BaseModel):
    msg_t: ClassVar[str] = "HotkeyTriggerResponse"
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
