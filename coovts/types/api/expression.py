from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..registry import request_model, response_model


class ExpressionParameter(BaseModel):
    name: str
    value: float


class HotkeyRef(BaseModel):
    name: str
    id: str


class ExpressionInfo(BaseModel):
    name: str
    file: str
    active: bool
    deactivate_when_key_is_let_go: bool
    auto_deactivate_after_seconds: bool
    seconds_remaining: float
    used_in_hotkeys: list[HotkeyRef] = []
    parameters: list[ExpressionParameter] = []


@request_model
class ExpressionStateRequest(BaseModel):
    msg_t: ClassVar[str] = "ExpressionStateRequest"
    details: bool = True
    expression_file: str | None = None


@response_model
class ExpressionStateResponse(BaseModel):
    msg_t: ClassVar[str] = "ExpressionStateResponse"
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    expressions: list[ExpressionInfo]


@request_model
class ExpressionActivationRequest(BaseModel):
    msg_t: ClassVar[str] = "ExpressionActivationRequest"
    expression_file: str
    fade_time: float = 0.25
    active: bool


@response_model
class ExpressionActivationResponse(BaseModel):
    msg_t: ClassVar[str] = "ExpressionActivationResponse"
