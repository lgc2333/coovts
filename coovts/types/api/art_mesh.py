from typing import ClassVar

from pydantic import BaseModel

from ..registry import (
    request_model,
    request_param_model,
    response_model,
    response_param_model,
)


@response_param_model
class ColorData(BaseModel):
    color_r: int
    color_g: int
    color_b: int
    color_a: int
    mix_with_scene_lighting_color: float = 1.0


@request_param_model
class ArtMeshMatcher(BaseModel):
    tint_all: bool = False
    art_mesh_number: list[int] = []
    name_exact: list[str] = []
    name_contains: list[str] = []
    tag_exact: list[str] = []
    tag_contains: list[str] = []


@request_model
class ArtMeshListRequest(BaseModel):
    msg_t: ClassVar[str] = "ArtMeshListRequest"


@response_model
class ArtMeshListResponse(BaseModel):
    msg_t: ClassVar[str] = "ArtMeshListResponse"
    model_loaded: bool
    number_of_art_mesh_names: int
    number_of_art_mesh_tags: int
    art_mesh_names: list[str]
    art_mesh_tags: list[str]


@request_model
class ColorTintRequest(BaseModel):
    msg_t: ClassVar[str] = "ColorTintRequest"
    color_tint: ColorData
    art_mesh_matcher: ArtMeshMatcher


@response_model
class ColorTintResponse(BaseModel):
    msg_t: ClassVar[str] = "ColorTintResponse"
    matched_art_meshes: int


@request_model
class ArtMeshSelectionRequest(BaseModel):
    msg_t: ClassVar[str] = "ArtMeshSelectionRequest"
    text_override: str | None = None
    help_override: str | None = None
    requested_art_mesh_count: int = 0
    active_art_meshes: list[str] = []


@response_model
class ArtMeshSelectionResponse(BaseModel):
    msg_t: ClassVar[str] = "ArtMeshSelectionResponse"
    success: bool
    active_art_meshes: list[str]
    inactive_art_meshes: list[str]
