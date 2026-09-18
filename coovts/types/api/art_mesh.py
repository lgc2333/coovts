from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
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


@with_response_model_config
class Point2D(BaseModel):
    x: float
    y: float


@with_response_model_config
class ArtMeshHitInfo(BaseModel):
    model_id: Annotated[str, Field(alias="modelID")]
    art_mesh_id: Annotated[str, Field(alias="artMeshID")]
    angle: float
    size: float
    vertex_id1: Annotated[int, Field(alias="vertexID1")]
    vertex_id2: Annotated[int, Field(alias="vertexID2")]
    vertex_id3: Annotated[int, Field(alias="vertexID3")]
    vertex_weight1: float
    vertex_weight2: float
    vertex_weight3: float


@with_response_model_config
class ArtMeshHit(BaseModel):
    art_mesh_order: int
    is_masked: bool
    hit_info: ArtMeshHitInfo


@with_request_model_config
class ArtMeshAtPositionRequest(BaseModel):
    """Only available on the public beta branch of VTube Studio."""

    x: float
    y: float
    visualize: float = 0


@with_response_model_config
class ArtMeshAtPositionResponse(BaseModel):
    """Only available on the public beta branch of VTube Studio."""

    model_loaded: bool
    loaded_model_id: Annotated[str, Field(alias="loadedModelID")]
    loaded_model_name: str
    model_was_hit: bool
    checked_position: Point2D
    window_size: Point2D
    art_mesh_hit_count: int
    art_mesh_hits: list[ArtMeshHit]
