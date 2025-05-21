from typing import Annotated, ClassVar, Literal

from pydantic import BaseModel, Field

from ..registry import request_model, response_model


class InputParameter(BaseModel):
    name: str
    added_by: str
    value: float
    min: float
    max: float
    default_value: float


class Live2DParameter(BaseModel):
    name: str
    value: float
    min: float
    max: float
    default_value: float


class ParameterValue(BaseModel):
    id: str
    value: float
    weight: float = 1.0


@request_model
class FaceFoundRequest(BaseModel):
    msg_t: ClassVar[str] = "FaceFoundRequest"


@response_model
class FaceFoundResponse(BaseModel):
    msg_t: ClassVar[str] = "FaceFoundResponse"
    found: bool


@request_model
class InputParameterListRequest(BaseModel):
    msg_t: ClassVar[str] = "InputParameterListRequest"


@response_model
class InputParameterListResponse(BaseModel):
    msg_t: ClassVar[str] = "InputParameterListResponse"
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    custom_parameters: list[InputParameter]
    default_parameters: list[InputParameter]


@request_model
class ParameterValueRequest(BaseModel):
    msg_t: ClassVar[str] = "ParameterValueRequest"
    name: str


@response_model
class ParameterValueResponse(InputParameter):
    msg_t: ClassVar[str] = "ParameterValueResponse"


@request_model
class Live2DParameterListRequest(BaseModel):
    msg_t: ClassVar[str] = "Live2DParameterListRequest"


@response_model
class Live2DParameterListResponse(BaseModel):
    msg_t: ClassVar[str] = "Live2DParameterListResponse"
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    parameters: list[Live2DParameter]


@request_model
class ParameterCreationRequest(BaseModel):
    msg_t: ClassVar[str] = "ParameterCreationRequest"
    parameter_name: str
    explanation: str = ""
    min: float
    max: float
    default_value: float


@response_model
class ParameterCreationResponse(BaseModel):
    msg_t: ClassVar[str] = "ParameterCreationResponse"
    parameter_name: str


@request_model
class ParameterDeletionRequest(BaseModel):
    msg_t: ClassVar[str] = "ParameterDeletionRequest"
    parameter_name: str


@response_model
class ParameterDeletionResponse(BaseModel):
    msg_t: ClassVar[str] = "ParameterDeletionResponse"
    parameter_name: str


@request_model
class InjectParameterDataRequest(BaseModel):
    msg_t: ClassVar[str] = "InjectParameterDataRequest"
    face_found: bool = False
    mode: Literal["set", "add"] = "set"
    parameter_values: list[ParameterValue]


@response_model
class InjectParameterDataResponse(BaseModel):
    msg_t: ClassVar[str] = "InjectParameterDataResponse"
