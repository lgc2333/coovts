from typing import Annotated

from pydantic import Field

from ..shared import VTSBaseModel


class APIStateRequest(VTSBaseModel):
    pass


class APIStateResponse(VTSBaseModel):
    active: bool
    vtube_studio_version: Annotated[str, Field(alias="vTubeStudioVersion")]
    current_session_authenticated: bool


class StatisticsRequest(VTSBaseModel):
    pass


class StatisticsResponse(VTSBaseModel):
    uptime: int
    framerate: int
    vtube_studio_version: Annotated[str, Field(alias="vTubeStudioVersion")]
    allowed_plugins: int
    connected_plugins: int
    started_with_steam: bool
    window_width: int
    window_height: int
    window_is_fullscreen: bool


class VTSFolderInfoRequest(VTSBaseModel):
    pass


class VTSFolderInfoResponse(VTSBaseModel):
    models: str
    backgrounds: str
    items: str
    config: str
    logs: str
    backup: str
