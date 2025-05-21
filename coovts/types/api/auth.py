from typing import ClassVar

from pydantic import BaseModel

from ..registry import request_model, response_model


@request_model
class AuthenticationTokenRequest(BaseModel):
    msg_t: ClassVar[str] = "AuthenticationTokenRequest"
    plugin_name: str
    plugin_developer: str
    plugin_icon: str | None = None
    """128x128 PNG or JPG base64"""


@response_model
class AuthenticationTokenResponse(BaseModel):
    msg_t: ClassVar[str] = "AuthenticationTokenResponse"
    authentication_token: str


@request_model
class AuthenticationRequest(BaseModel):
    msg_t: ClassVar[str] = "AuthenticationRequest"
    plugin_name: str
    plugin_developer: str
    authentication_token: str


@response_model
class AuthenticationResponse(BaseModel):
    msg_t: ClassVar[str] = "AuthenticationResponse"
    authenticated: bool
    reason: str
