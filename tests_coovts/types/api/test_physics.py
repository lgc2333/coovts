"""Wire-shape tests for the physics models of `coovts.types.api`."""

import json

from coovts.types.api import (
    GetCurrentModelPhysicsRequest,
    GetCurrentModelPhysicsResponse,
    PhysicsGroup,
    PhysicsOverride,
    SetCurrentModelPhysicsRequest,
)


def test_documented_response_payload_decodes() -> None:
    """The example response from the reference docs decodes into the expected models."""
    response = GetCurrentModelPhysicsResponse.model_validate(
        {
            "modelLoaded": True,
            "modelName": "My Currently Loaded Model",
            "modelID": "UniqueIDOfModel",
            "modelHasPhysics": True,
            "physicsSwitchedOn": True,
            "usingLegacyPhysics": False,
            "physicsFPSSetting": -1,
            "baseStrength": 50,
            "baseWind": 17,
            "apiPhysicsOverrideActive": False,
            "apiPhysicsOverridePluginName": "",
            "physicsGroups": [
                {
                    "groupID": "PhysicsSetting1",
                    "groupName": "Hair Front Physics",
                    "strengthMultiplier": 1.5,
                    "windMultiplier": 0.3,
                },
                {
                    "groupID": "PhysicsSetting2",
                    "groupName": "Clothes Physics",
                    "strengthMultiplier": 1,
                    "windMultiplier": 2,
                },
            ],
        },
    )

    assert response.model_id == "UniqueIDOfModel"
    assert response.physics_fps_setting == -1
    assert response.base_strength == 50
    assert [
        (group.group_id, group.group_name) for group in response.physics_groups
    ] == [
        ("PhysicsSetting1", "Hair Front Physics"),
        ("PhysicsSetting2", "Clothes Physics"),
    ]


def test_physics_group_dumps_the_wire_shape() -> None:
    """A physics group carries its `groupID` and multiplier aliases on the wire."""
    group = PhysicsGroup(
        group_id="PhysicsSetting1",
        group_name="Hair Front Physics",
        strength_multiplier=1.5,
        wind_multiplier=0.3,
    )

    assert json.loads(group.model_dump_json()) == {
        "groupID": "PhysicsSetting1",
        "groupName": "Hair Front Physics",
        "strengthMultiplier": 1.5,
        "windMultiplier": 0.3,
    }


def test_physics_override_dumps_base_value_and_timer() -> None:
    """A physics override emits `setBaseValue` and `overrideSeconds` aliases."""
    override = PhysicsOverride(
        id="PhysicsSetting1",
        value=1.5,
        set_base_value=False,
        override_seconds=2.0,
    )

    assert json.loads(override.model_dump_json()) == {
        "id": "PhysicsSetting1",
        "value": 1.5,
        "setBaseValue": False,
        "overrideSeconds": 2.0,
    }


def test_set_request_built_from_field_names_dumps_overrides() -> None:
    """An override request built from python field names emits the wire arrays."""
    request = SetCurrentModelPhysicsRequest(
        strength_overrides=[
            PhysicsOverride(
                id="PhysicsSetting1",
                value=1.5,
                set_base_value=False,
                override_seconds=2.0,
            ),
        ],
        wind_overrides=[
            PhysicsOverride(
                id="",
                value=85,
                set_base_value=True,
                override_seconds=5.0,
            ),
        ],
    )

    assert json.loads(request.model_dump_json()) == {
        "strengthOverrides": [
            {
                "id": "PhysicsSetting1",
                "value": 1.5,
                "setBaseValue": False,
                "overrideSeconds": 2.0,
            },
        ],
        "windOverrides": [
            {
                "id": "",
                "value": 85,
                "setBaseValue": True,
                "overrideSeconds": 5.0,
            },
        ],
    }


def test_bare_requests_emit_the_wire_shape() -> None:
    """A default physics write and the physics read carry no payload fields."""
    assert json.loads(SetCurrentModelPhysicsRequest().model_dump_json()) == {
        "strengthOverrides": [],
        "windOverrides": [],
    }
    assert json.loads(GetCurrentModelPhysicsRequest().model_dump_json()) == {}
