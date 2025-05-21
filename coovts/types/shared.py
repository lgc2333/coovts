from typing import Annotated, Any

from cookit.pyd import model_with_model_config
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

request_model_config = ConfigDict(
    alias_generator=to_camel,
    validate_by_alias=False,
    serialize_by_alias=True,
)
response_model_config = ConfigDict(
    alias_generator=to_camel,
)


@model_with_model_config(request_model_config)
class BaseRequest(BaseModel):
    api_name: str = "VTubeStudioPublicAPI"
    api_version: str = "1.0"
    request_id: Annotated[str | None, Field(alias="requestID")] = None
    message_type: str
    data: Any


@model_with_model_config(response_model_config)
class BaseResponse(BaseModel):
    api_name: str
    api_version: str = "1.0"
    timestamp: int
    """13 digits"""
    request_id: Annotated[str | None, Field(alias="requestID")]
    message_type: str
    data: Any
