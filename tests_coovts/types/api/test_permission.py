"""Wire-shape tests for the permission models of `coovts.types.api`."""

import json

from coovts.types.api import PermissionRequest, PermissionResponse
from coovts.types.shared import get_message_type

from ...utils.frames import real_payload


def test_documented_response_payload_decodes() -> None:
    """The example response from the reference docs decodes into the expected models."""
    response = PermissionResponse.model_validate(
        {
            "grantSuccess": True,
            "requestedPermission": "LoadCustomImagesAsItems",
            "permissions": [{"name": "LoadCustomImagesAsItems", "granted": True}],
        },
    )

    assert response.grant_success is True
    assert response.requested_permission == "LoadCustomImagesAsItems"
    assert [(info.name, info.granted) for info in response.permissions] == [
        ("LoadCustomImagesAsItems", True),
    ]


def test_real_list_only_response_decodes() -> None:
    """A real VTube Studio answers a list-only request with `grantSuccess: false` and no name."""
    response = PermissionResponse.model_validate(
        real_payload("PermissionResponse"),
    )

    assert response.grant_success is False
    assert response.requested_permission == ""
    assert [(info.name, info.granted) for info in response.permissions] == [
        ("LoadCustomImagesAsItems", False),
    ]


def test_unknown_extra_fields_are_ignored() -> None:
    """Permission fields a future VTS adds, at either level, do not break the decode."""
    response = PermissionResponse.model_validate(
        {
            "someNewTopLevelField": 1,
            "permissions": [
                {"name": "ControlNDISettings", "granted": True, "icon": "icon.png"},
            ],
        },
    )

    assert response.permissions[0].granted is True
    assert response.permissions[0].name == "ControlNDISettings"


def test_empty_request_emits_the_wire_shape() -> None:
    """A bare request carries the empty permission alias under its own message type."""
    assert json.loads(PermissionRequest().model_dump_json()) == {
        "requestedPermission": "",
    }
    assert get_message_type(PermissionRequest) == "PermissionRequest"
