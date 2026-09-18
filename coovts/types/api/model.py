from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class ModelPosition(VTSBaseModel):
    position_x: float
    position_y: float
    rotation: float
    size: float


class ModelInfo(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    vts_model_name: str
    vts_model_icon_name: str


class CurrentModelRequest(VTSBaseModel):
    pass


class CurrentModelResponse(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    vts_model_name: str
    vts_model_icon_name: str
    live2d_model_name: str
    model_load_time: int  # milliseconds
    time_since_model_loaded: int  # milliseconds
    number_of_live2d_parameters: int
    number_of_live2d_artmeshes: int
    has_physics_file: bool
    number_of_textures: int
    texture_resolution: int
    model_position: ModelPosition


class AvailableModelsRequest(VTSBaseModel):
    pass


class AvailableModelsResponse(VTSBaseModel):
    number_of_models: int
    available_models: list[ModelInfo]


class ModelLoadRequest(VTSBaseModel):
    model_id: Annotated[str, Field(alias="modelID")]


class ModelLoadResponse(VTSBaseModel):
    model_id: Annotated[str, Field(alias="modelID")]


class MoveModelRequest(VTSBaseModel):
    time_in_seconds: float
    values_are_relative_to_model: bool
    position_x: float | None = None
    position_y: float | None = None
    rotation: float | None = None
    size: float | None = None


class MoveModelResponse(VTSBaseModel):
    pass
