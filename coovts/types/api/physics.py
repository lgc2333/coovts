from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..registry import (
    request_model,
    request_param_model,
    response_model,
    response_param_model,
)


@request_param_model
class PhysicsOverride(BaseModel):
    id: str
    value: float
    set_base_value: bool
    override_seconds: float


@response_param_model
class PhysicsGroup(BaseModel):
    group_id: Annotated[str, Field(alias="groupID")]
    group_name: str
    strength_multiplier: float
    wind_multiplier: float


@request_model
class GetCurrentModelPhysicsRequest(BaseModel):
    msg_t: ClassVar[str] = "GetCurrentModelPhysicsRequest"


@response_model
class GetCurrentModelPhysicsResponse(BaseModel):
    msg_t: ClassVar[str] = "GetCurrentModelPhysicsResponse"
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    model_has_physics: bool
    physics_switched_on: bool
    using_legacy_physics: bool
    physics_fps_setting: int
    base_strength: int
    base_wind: int
    api_physics_override_active: bool
    api_physics_override_plugin_name: str
    physics_groups: list[PhysicsGroup]


@request_model
class SetCurrentModelPhysicsRequest(BaseModel):
    msg_t: ClassVar[str] = "SetCurrentModelPhysicsRequest"
    strength_overrides: list[PhysicsOverride] = []
    wind_overrides: list[PhysicsOverride] = []


@response_model
class SetCurrentModelPhysicsResponse(BaseModel):
    msg_t: ClassVar[str] = "SetCurrentModelPhysicsResponse"
