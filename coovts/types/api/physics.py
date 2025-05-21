from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class PhysicsOverride(BaseModel):
    id: str
    value: float
    set_base_value: bool
    override_seconds: float


@with_response_model_config
class PhysicsGroup(BaseModel):
    group_id: Annotated[str, Field(alias="groupID")]
    group_name: str
    strength_multiplier: float
    wind_multiplier: float


@with_request_model_config
class GetCurrentModelPhysicsRequest(BaseModel):
    pass


@with_response_model_config
class GetCurrentModelPhysicsResponse(BaseModel):
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


@with_request_model_config
class SetCurrentModelPhysicsRequest(BaseModel):
    strength_overrides: list[PhysicsOverride] = []
    wind_overrides: list[PhysicsOverride] = []


@with_response_model_config
class SetCurrentModelPhysicsResponse(BaseModel):
    pass
