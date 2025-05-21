from pydantic import BaseModel

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class AuthenticationTokenRequest(BaseModel):
    plugin_name: str
    plugin_developer: str
    plugin_icon: str | None = None
    """128x128 PNG or JPG base64"""


@with_response_model_config
class AuthenticationTokenResponse(BaseModel):
    authentication_token: str


@with_request_model_config
class AuthenticationRequest(BaseModel):
    plugin_name: str
    plugin_developer: str
    authentication_token: str


@with_response_model_config
class AuthenticationResponse(BaseModel):
    authenticated: bool
    reason: str
