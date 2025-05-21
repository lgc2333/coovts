from pydantic import BaseModel

from ..shared import with_request_model_config, with_response_model_config


@with_request_model_config
class APIStateRequest(BaseModel):
    pass


@with_response_model_config
class APIStateResponse(BaseModel):
    active: bool
    v_tube_studio_version: str
    current_session_authenticated: bool


@with_request_model_config
class StatisticsRequest(BaseModel):
    pass


@with_response_model_config
class StatisticsResponse(BaseModel):
    uptime: int
    framerate: int
    v_tube_studio_version: str
    allowed_plugins: int
    connected_plugins: int
    started_with_steam: bool
    window_width: int
    window_height: int
    window_is_fullscreen: bool


@with_request_model_config
class VTSFolderInfoRequest(BaseModel):
    pass


@with_response_model_config
class VTSFolderInfoResponse(BaseModel):
    models: str
    backgrounds: str
    items: str
    config: str
    logs: str
    backup: str
