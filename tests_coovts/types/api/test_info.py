"""Wire-shape tests for the info models of `coovts.types.api`."""

import json

from coovts.types.api import (
    APIStateRequest,
    APIStateResponse,
    StatisticsRequest,
    StatisticsResponse,
    VTSFolderInfoRequest,
    VTSFolderInfoResponse,
)


def test_documented_api_state_response_decodes() -> None:
    """The example API state response decodes into the expected models."""
    response = APIStateResponse.model_validate(
        {
            "active": True,
            "vTubeStudioVersion": "1.9.0",
            "currentSessionAuthenticated": False,
        },
    )

    assert response.active is True
    assert response.vtube_studio_version == "1.9.0"
    assert response.current_session_authenticated is False


def test_documented_statistics_response_decodes() -> None:
    """The example statistics response decodes into the expected models."""
    response = StatisticsResponse.model_validate(
        {
            "uptime": 1439384,
            "framerate": 73,
            "vTubeStudioVersion": "1.9.0",
            "allowedPlugins": 7,
            "connectedPlugins": 2,
            "startedWithSteam": True,
            "windowWidth": 1031,
            "windowHeight": 812,
            "windowIsFullscreen": False,
        },
    )

    assert response.uptime == 1439384
    assert response.framerate == 73
    assert response.vtube_studio_version == "1.9.0"
    assert response.allowed_plugins == 7
    assert response.connected_plugins == 2
    assert response.started_with_steam is True
    assert response.window_width == 1031
    assert response.window_height == 812
    assert response.window_is_fullscreen is False


def test_statistics_response_emits_the_wire_shape() -> None:
    """The version alias and window fields survive a dump unchanged."""
    response = StatisticsResponse.model_validate(
        {
            "uptime": 1439384,
            "framerate": 73,
            "vTubeStudioVersion": "1.9.0",
            "allowedPlugins": 7,
            "connectedPlugins": 2,
            "startedWithSteam": True,
            "windowWidth": 1031,
            "windowHeight": 812,
            "windowIsFullscreen": False,
        },
    )

    assert json.loads(response.model_dump_json()) == {
        "uptime": 1439384,
        "framerate": 73,
        "vTubeStudioVersion": "1.9.0",
        "allowedPlugins": 7,
        "connectedPlugins": 2,
        "startedWithSteam": True,
        "windowWidth": 1031,
        "windowHeight": 812,
        "windowIsFullscreen": False,
    }


def test_documented_folder_info_response_decodes() -> None:
    """The example folder response decodes into the expected models."""
    response = VTSFolderInfoResponse.model_validate(
        {
            "models": "Live2DModels",
            "backgrounds": "Backgrounds",
            "items": "Items",
            "config": "Config",
            "logs": "Logs",
            "backup": "Backup",
        },
    )

    assert response.models == "Live2DModels"
    assert response.backgrounds == "Backgrounds"
    assert response.items == "Items"
    assert response.config == "Config"
    assert response.logs == "Logs"
    assert response.backup == "Backup"


def test_bare_requests_emit_an_empty_data_object() -> None:
    """The three info requests carry no payload fields at all."""
    for request in (APIStateRequest(), StatisticsRequest(), VTSFolderInfoRequest()):
        assert json.loads(request.model_dump_json()) == {}
