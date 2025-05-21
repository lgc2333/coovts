from typing import Annotated

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config


@with_response_model_config
class ModelPosition(BaseModel):
    position_x: float
    position_y: float
    rotation: float
    size: float


@with_response_model_config
class ModelInfo(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    vts_model_name: str
    vts_model_icon_name: str


@with_request_model_config
class CurrentModelRequest(BaseModel):
    pass


@with_response_model_config
class CurrentModelResponse(BaseModel):
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


@with_request_model_config
class AvailableModelsRequest(BaseModel):
    pass


@with_response_model_config
class AvailableModelsResponse(BaseModel):
    number_of_models: int
    available_models: list[ModelInfo]


@with_request_model_config
class ModelLoadRequest(BaseModel):
    model_id: Annotated[str, Field(alias="modelID")]


@with_response_model_config
class ModelLoadResponse(BaseModel):
    model_id: Annotated[str, Field(alias="modelID")]


@with_request_model_config
class MoveModelRequest(BaseModel):
    time_in_seconds: float
    values_are_relative_to_model: bool
    position_x: float | None = None
    position_y: float | None = None
    rotation: float | None = None
    size: float | None = None


@with_response_model_config
class MoveModelResponse(BaseModel):
    pass
