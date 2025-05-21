from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config


@with_response_model_config
class ExpressionParameter(BaseModel):
    name: str
    value: float


@with_response_model_config
class HotkeyRef(BaseModel):
    name: str
    id: str


@with_response_model_config
class ExpressionInfo(BaseModel):
    name: str
    file: str
    active: bool
    deactivate_when_key_is_let_go: bool
    auto_deactivate_after_seconds: bool
    seconds_remaining: float
    used_in_hotkeys: list[HotkeyRef] = []
    parameters: list[ExpressionParameter] = []


@with_request_model_config
class ExpressionStateRequest(BaseModel):
    details: bool = True
    expression_file: str | None = None


@with_response_model_config
class ExpressionStateResponse(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    expressions: list[ExpressionInfo]


@with_request_model_config
class ExpressionActivationRequest(BaseModel):
    expression_file: str
    fade_time: float = 0.25
    active: bool


@with_response_model_config
class ExpressionActivationResponse(BaseModel):
    pass
