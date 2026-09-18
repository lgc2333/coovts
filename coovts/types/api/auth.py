from ..shared import VTSBaseModel


class AuthenticationTokenRequest(VTSBaseModel):
    plugin_name: str
    plugin_developer: str
    plugin_icon: str | None = None
    """128x128 PNG or JPG base64"""


class AuthenticationTokenResponse(VTSBaseModel):
    authentication_token: str


class AuthenticationRequest(VTSBaseModel):
    plugin_name: str
    plugin_developer: str
    authentication_token: str


class AuthenticationResponse(VTSBaseModel):
    authenticated: bool
    reason: str
