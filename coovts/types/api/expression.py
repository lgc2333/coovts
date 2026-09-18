from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class ExpressionParameter(VTSBaseModel):
    name: str
    value: float


class HotkeyRef(VTSBaseModel):
    name: str
    id: str


class ExpressionInfo(VTSBaseModel):
    name: str
    file: str
    active: bool
    deactivate_when_key_is_let_go: bool
    auto_deactivate_after_seconds: bool
    seconds_remaining: float
    used_in_hotkeys: list[HotkeyRef] = []
    parameters: list[ExpressionParameter] = []


class ExpressionStateRequest(VTSBaseModel):
    details: bool = True
    expression_file: str | None = None


class ExpressionStateResponse(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    expressions: list[ExpressionInfo]


class ExpressionActivationRequest(VTSBaseModel):
    expression_file: str
    fade_time: float = 0.25
    active: bool


class ExpressionActivationResponse(VTSBaseModel):
    pass
