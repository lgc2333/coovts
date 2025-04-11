from typing import Annotated, Any

from cookit.pyd import model_with_model_config
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

request_model_config = ConfigDict(
    alias_generator=to_camel,
    validate_by_alias=False,
    serialize_by_alias=True,
)


@model_with_model_config(request_model_config)
class BaseRequest(BaseModel):
    api_name: str = "VTubeStudioPublicAPI"
    api_version: str = "1.0"
    request_id: Annotated[str | None, Field(alias="requestID")] = None
    message_type: str
    data: Any


@model_with_model_config(request_model_config)
class AuthenticationTokenRequestData(BaseModel):
    plugin_name: str
    plugin_developer: str
    plugin_icon: str | None = None
    """128x128 PNG or JPG base64"""


@model_with_model_config(request_model_config)
class AuthenticationRequestData(BaseModel):
    plugin_name: str
    plugin_developer: str
    authentication_token: str


@model_with_model_config(request_model_config)
class EventSubscriptionRequestData(BaseModel):
    event_name: str
    subscribe: bool
    config: Any


@model_with_model_config(request_model_config)
class ParameterValueRequestData(BaseModel):
    name: str
