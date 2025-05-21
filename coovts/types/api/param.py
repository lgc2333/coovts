from typing import Annotated, Literal

from pydantic import BaseModel, Field

from ..shared import with_request_model_config, with_response_model_config

type ParameterMode = Literal["set", "add"]


@with_request_model_config
class ParameterValue(BaseModel):
    id: str
    value: float
    weight: float = 1.0


@with_response_model_config
class InputParameter(BaseModel):
    name: str
    added_by: str
    value: float
    min: float
    max: float
    default_value: float


@with_response_model_config
class Live2DParameter(BaseModel):
    name: str
    value: float
    min: float
    max: float
    default_value: float


@with_request_model_config
class FaceFoundRequest(BaseModel):
    pass


@with_response_model_config
class FaceFoundResponse(BaseModel):
    found: bool


@with_request_model_config
class InputParameterListRequest(BaseModel):
    pass


@with_response_model_config
class InputParameterListResponse(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    custom_parameters: list[InputParameter]
    default_parameters: list[InputParameter]


@with_request_model_config
class ParameterValueRequest(BaseModel):
    name: str


@with_response_model_config
class ParameterValueResponse(InputParameter):
    pass


@with_request_model_config
class Live2DParameterListRequest(BaseModel):
    pass


@with_response_model_config
class Live2DParameterListResponse(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    parameters: list[Live2DParameter]


@with_request_model_config
class ParameterCreationRequest(BaseModel):
    parameter_name: str
    explanation: str = ""
    min: float
    max: float
    default_value: float


@with_response_model_config
class ParameterCreationResponse(BaseModel):
    parameter_name: str


@with_request_model_config
class ParameterDeletionRequest(BaseModel):
    parameter_name: str


@with_response_model_config
class ParameterDeletionResponse(BaseModel):
    parameter_name: str


@with_request_model_config
class InjectParameterDataRequest(BaseModel):
    face_found: bool = False
    mode: ParameterMode = "set"
    parameter_values: list[ParameterValue]


@with_response_model_config
class InjectParameterDataResponse(BaseModel):
    pass
