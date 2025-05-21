from pydantic import BaseModel

from ..shared import with_request_model_config, with_response_model_config


@with_response_model_config
class ColorData(BaseModel):
    color_r: int
    color_g: int
    color_b: int
    color_a: int
    mix_with_scene_lighting_color: float = 1.0


@with_request_model_config
class ArtMeshMatcher(BaseModel):
    tint_all: bool = False
    art_mesh_number: list[int] = []
    name_exact: list[str] = []
    name_contains: list[str] = []
    tag_exact: list[str] = []
    tag_contains: list[str] = []


@with_request_model_config
class ArtMeshListRequest(BaseModel):
    pass


@with_response_model_config
class ArtMeshListResponse(BaseModel):
    model_loaded: bool
    number_of_art_mesh_names: int
    number_of_art_mesh_tags: int
    art_mesh_names: list[str]
    art_mesh_tags: list[str]


@with_request_model_config
class ColorTintRequest(BaseModel):
    color_tint: ColorData
    art_mesh_matcher: ArtMeshMatcher


@with_response_model_config
class ColorTintResponse(BaseModel):
    matched_art_meshes: int


@with_request_model_config
class ArtMeshSelectionRequest(BaseModel):
    text_override: str | None = None
    help_override: str | None = None
    requested_art_mesh_count: int = 0
    active_art_meshes: list[str] = []


@with_response_model_config
class ArtMeshSelectionResponse(BaseModel):
    success: bool
    active_art_meshes: list[str]
    inactive_art_meshes: list[str]
