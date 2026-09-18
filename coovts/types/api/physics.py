from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class PhysicsOverride(VTSBaseModel):
    id: str
    value: float
    set_base_value: bool
    override_seconds: float


class PhysicsGroup(VTSBaseModel):
    group_id: Annotated[str, Field(alias="groupID")]
    group_name: str
    strength_multiplier: float
    wind_multiplier: float


class GetCurrentModelPhysicsRequest(VTSBaseModel):
    pass


class GetCurrentModelPhysicsResponse(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    model_has_physics: bool
    physics_switched_on: bool
    using_legacy_physics: bool
    physics_fps_setting: Annotated[int, Field(alias="physicsFPSSetting")]
    base_strength: int
    base_wind: int
    api_physics_override_active: bool
    api_physics_override_plugin_name: str
    physics_groups: list[PhysicsGroup]


class SetCurrentModelPhysicsRequest(VTSBaseModel):
    strength_overrides: list[PhysicsOverride] = []
    wind_overrides: list[PhysicsOverride] = []


class SetCurrentModelPhysicsResponse(VTSBaseModel):
    pass
