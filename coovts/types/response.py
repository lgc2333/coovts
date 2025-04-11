from typing import Annotated, Any

from cookit.pyd import model_with_model_config
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

response_model_config = ConfigDict(alias_generator=to_camel)


@model_with_model_config(response_model_config)
class BaseResponse(BaseModel):
    api_name: str
    api_version: str = "1.0"
    timestamp: int
    """13 digits"""
    request_id: Annotated[str | None, Field(alias="requestID")]
    message_type: str
    data: Any


@model_with_model_config(response_model_config)
class APIErrorResponseData(BaseModel):
    error_id: Annotated[int, Field(alias="errorID")]
    message: str


@model_with_model_config(response_model_config)
class AuthenticationTokenResponseData(BaseModel):
    authentication_token: str


@model_with_model_config(response_model_config)
class AuthenticationResponseData(BaseModel):
    authenticated: bool
    reason: str


@model_with_model_config(response_model_config)
class ParameterValueResponseData(BaseModel):
    name: str
    added_by: str
    value: float
    min: float
    max: float
    default_value: float


@model_with_model_config(response_model_config)
class InputParameterListResponseData(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    custom_parameters: list[ParameterValueResponseData]
    default_parameters: list[ParameterValueResponseData]


@model_with_model_config(response_model_config)
class Live2DParameter(BaseModel):
    name: str
    value: float
    min: float
    max: float
    default_value: float


@model_with_model_config(response_model_config)
class Live2DParameterListResponseData(BaseModel):
    model_loaded: bool
    model_name: str
    model_id: Annotated[str, Field(alias="modelID")]
    parameters: list[Live2DParameter]
