from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config


@with_response_model_config
class HotkeyInfo(BaseModel):
    name: str
    type: str
    description: str
    file: str
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    key_combination: list[str]
    on_screen_button_id: Annotated[int, Field(alias="onScreenButtonID")]


@with_request_model_config
class HotkeysInCurrentModelRequest(BaseModel):
    model_id: Annotated[str | None, Field(alias="modelID")] = None
    live2d_item_file_name: Annotated[
        str | None,
        Field(alias="live2DItemFileName"),
    ] = None


@with_response_model_config
class HotkeysInCurrentModelResponse(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    available_hotkeys: list[HotkeyInfo]


@with_request_model_config
class HotkeyTriggerRequest(BaseModel):
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
    item_instance_id: Annotated[str | None, Field(alias="itemInstanceID")] = None


@with_response_model_config
class HotkeyTriggerResponse(BaseModel):
    hotkey_id: Annotated[str, Field(alias="hotkeyID")]
