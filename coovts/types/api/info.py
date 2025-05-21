from typing import ClassVar

from pydantic import BaseModel

from ..registry import request_model, response_model


@request_model
class APIStateRequest(BaseModel):
    msg_t: ClassVar[str] = "APIStateRequest"


@response_model
class APIStateResponse(BaseModel):
    msg_t: ClassVar[str] = "APIStateResponse"
    active: bool
    v_tube_studio_version: str
    current_session_authenticated: bool


@request_model
class StatisticsRequest(BaseModel):
    msg_t: ClassVar[str] = "StatisticsRequest"


@response_model
class StatisticsResponse(BaseModel):
    msg_t: ClassVar[str] = "StatisticsResponse"
    uptime: int
    framerate: int
    v_tube_studio_version: str
    allowed_plugins: int
    connected_plugins: int
    started_with_steam: bool
    window_width: int
    window_height: int
    window_is_fullscreen: bool


@request_model
class VTSFolderInfoRequest(BaseModel):
    msg_t: ClassVar[str] = "VTSFolderInfoRequest"


@response_model
class VTSFolderInfoResponse(BaseModel):
    msg_t: ClassVar[str] = "VTSFolderInfoResponse"
    models: str
    backgrounds: str
    items: str
    config: str
    logs: str
    backup: str
