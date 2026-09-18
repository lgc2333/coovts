from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class ColorData(VTSBaseModel):
    color_r: int
    color_g: int
    color_b: int
    color_a: int
    mix_with_scene_lighting_color: float = 1.0


class ArtMeshMatcher(VTSBaseModel):
    tint_all: bool = False
    art_mesh_number: list[int] = []
    name_exact: list[str] = []
    name_contains: list[str] = []
    tag_exact: list[str] = []
    tag_contains: list[str] = []


class ArtMeshListRequest(VTSBaseModel):
    pass


class ArtMeshListResponse(VTSBaseModel):
    model_loaded: bool
    number_of_art_mesh_names: int
    number_of_art_mesh_tags: int
    art_mesh_names: list[str]
    art_mesh_tags: list[str]


class ColorTintRequest(VTSBaseModel):
    color_tint: ColorData
    art_mesh_matcher: ArtMeshMatcher


class ColorTintResponse(VTSBaseModel):
    matched_art_meshes: int


class ArtMeshSelectionRequest(VTSBaseModel):
    text_override: str | None = None
    help_override: str | None = None
    requested_art_mesh_count: int = 0
    active_art_meshes: list[str] = []


class ArtMeshSelectionResponse(VTSBaseModel):
    success: bool
    active_art_meshes: list[str]
    inactive_art_meshes: list[str]


class Point2D(VTSBaseModel):
    x: float
    y: float


class ArtMeshHitInfo(VTSBaseModel):
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


class ArtMeshHit(VTSBaseModel):
    art_mesh_order: int
    is_masked: bool
    hit_info: ArtMeshHitInfo


class ArtMeshAtPositionRequest(VTSBaseModel):
    """Only available on the public beta branch of VTube Studio."""

    x: float
    y: float
    visualize: float = 0


class ArtMeshAtPositionResponse(VTSBaseModel):
    """Only available on the public beta branch of VTube Studio."""

    model_loaded: bool
    loaded_model_id: Annotated[str, Field(alias="loadedModelID")]
    loaded_model_name: str
    model_was_hit: bool
    checked_position: Point2D
    window_size: Point2D
    art_mesh_hit_count: int
    art_mesh_hits: list[ArtMeshHit]
