from typing import Annotated, Literal

from pydantic import Field

from ..shared import VTSBaseModel

type ParameterMode = Literal["set", "add"]


class ParameterValue(VTSBaseModel):
    id: str
    value: float
    weight: float = 1.0


class InputParameter(VTSBaseModel):
    name: str
    added_by: str
    value: float
    min: float
    max: float
    default_value: float


class Live2DParameter(VTSBaseModel):
    name: str
    value: float
    min: float
    max: float
    default_value: float


class FaceFoundRequest(VTSBaseModel):
    pass


class FaceFoundResponse(VTSBaseModel):
    found: bool


class InputParameterListRequest(VTSBaseModel):
    pass


class InputParameterListResponse(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    custom_parameters: list[InputParameter]
    default_parameters: list[InputParameter]


class ParameterValueRequest(VTSBaseModel):
    name: str


class ParameterValueResponse(InputParameter):
    pass


class Live2DParameterListRequest(VTSBaseModel):
    pass


class Live2DParameterListResponse(VTSBaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    parameters: list[Live2DParameter]


class ParameterCreationRequest(VTSBaseModel):
    parameter_name: str
    explanation: str = ""
    min: float
    max: float
    default_value: float


class ParameterCreationResponse(VTSBaseModel):
    parameter_name: str


class ParameterDeletionRequest(VTSBaseModel):
    parameter_name: str


class ParameterDeletionResponse(VTSBaseModel):
    parameter_name: str


class InjectParameterDataRequest(VTSBaseModel):
    face_found: bool = False
    mode: ParameterMode = "set"
    parameter_values: list[ParameterValue]


class InjectParameterDataResponse(VTSBaseModel):
    pass
