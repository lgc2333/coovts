from typing import Annotated, ClassVar

from pydantic import BaseModel, Field

from ..registry import request_model, response_model


class ModelPosition(BaseModel):
    position_x: float
    position_y: float
    rotation: float
    size: float


class ModelInfo(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    vts_model_name: str
    vts_model_icon_name: str


@request_model
class CurrentModelRequest(BaseModel):
    msg_t: ClassVar[str] = "CurrentModelRequest"


@response_model
class CurrentModelResponse(BaseModel):
    msg_t: ClassVar[str] = "CurrentModelResponse"
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


@request_model
class AvailableModelsRequest(BaseModel):
    msg_t: ClassVar[str] = "AvailableModelsRequest"


@response_model
class AvailableModelsResponse(BaseModel):
    msg_t: ClassVar[str] = "AvailableModelsResponse"
    number_of_models: int
    available_models: list[ModelInfo]


@request_model
class ModelLoadRequest(BaseModel):
    msg_t: ClassVar[str] = "ModelLoadRequest"
    model_id: Annotated[str, Field(alias="modelID")]


@response_model
class ModelLoadResponse(BaseModel):
    msg_t: ClassVar[str] = "ModelLoadResponse"
    model_id: Annotated[str, Field(alias="modelID")]


@request_model
class MoveModelRequest(BaseModel):
    msg_t: ClassVar[str] = "MoveModelRequest"
    time_in_seconds: float
    values_are_relative_to_model: bool
    position_x: float | None = None
    position_y: float | None = None
    rotation: float | None = None
    size: float | None = None


@response_model
class MoveModelResponse(BaseModel):
    msg_t: ClassVar[str] = "MoveModelResponse"
