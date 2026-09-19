"""Wire-shape tests for the hotkey models of `coovts.types.api`."""

import json

from coovts.types.api import (
    HotkeysInCurrentModelRequest,
    HotkeysInCurrentModelResponse,
    HotkeyTriggerRequest,
    HotkeyTriggerResponse,
)


def test_documented_response_payload_decodes() -> None:
    """The example response from the reference docs decodes into the expected models."""
    response = HotkeysInCurrentModelResponse.model_validate(
        {
            "modelLoaded": True,
            "modelName": "My Currently Loaded Model",
            "modelID": "UniqueIDOfModel",
            "availableHotkeys": [
                {
                    "name": "My first hotkey",
                    "type": "ToggleExpression",
                    "description": "Toggles an expression",
                    "file": "myExpression_1.exp3.json",
                    "hotkeyID": "SomeUniqueIdToIdentifyHotkeyWith1",
                    "keyCombination": [],
                    "onScreenButtonID": 8,
                },
                {
                    "name": "My fifth hotkey",
                    "type": "Unset",
                    "description": "No action set for hotkey",
                    "file": "",
                    "hotkeyID": "SomeUniqueIdToIdentifyHotkeyWith5",
                    "keyCombination": [],
                    "onScreenButtonID": 5,
                },
            ],
        },
    )

    assert response.model_loaded is True
    assert response.model_name == "My Currently Loaded Model"
    assert response.model_id == "UniqueIDOfModel"
    assert [
        (
            hotkey.name,
            hotkey.type,
            hotkey.description,
            hotkey.file,
            hotkey.hotkey_id,
            hotkey.key_combination,
            hotkey.on_screen_button_id,
        )
        for hotkey in response.available_hotkeys
    ] == [
        (
            "My first hotkey",
            "ToggleExpression",
            "Toggles an expression",
            "myExpression_1.exp3.json",
            "SomeUniqueIdToIdentifyHotkeyWith1",
            [],
            8,
        ),
        (
            "My fifth hotkey",
            "Unset",
            "No action set for hotkey",
            "",
            "SomeUniqueIdToIdentifyHotkeyWith5",
            [],
            5,
        ),
    ]


def test_documented_response_payload_emits_the_wire_shape() -> None:
    """A decoded hotkey keeps its ID aliases and always-empty key combination on the wire."""
    response = HotkeysInCurrentModelResponse.model_validate(
        {
            "modelLoaded": False,
            "modelName": "",
            "modelID": "",
            "availableHotkeys": [
                {
                    "name": "My hotkey",
                    "type": "MoveModel",
                    "description": "Moves the Live2D model",
                    "file": "",
                    "hotkeyID": "SomeUniqueIdToIdentifyHotkeyWith4",
                    "keyCombination": [],
                    "onScreenButtonID": -1,
                },
            ],
        },
    )

    assert json.loads(response.model_dump_json()) == {
        "modelLoaded": False,
        "modelName": "",
        "modelID": "",
        "availableHotkeys": [
            {
                "name": "My hotkey",
                "type": "MoveModel",
                "description": "Moves the Live2D model",
                "file": "",
                "hotkeyID": "SomeUniqueIdToIdentifyHotkeyWith4",
                "keyCombination": [],
                "onScreenButtonID": -1,
            },
        ],
    }


def test_empty_request_emits_the_wire_shape() -> None:
    """A bare request carries both optional item selectors as explicit nulls."""
    assert json.loads(HotkeysInCurrentModelRequest().model_dump_json()) == {
        "modelID": None,
        "live2DItemFileName": None,
    }


def test_request_fields_round_trip_through_wire_keys() -> None:
    """The documented request keys map onto the python field names."""
    request = HotkeysInCurrentModelRequest.model_validate(
        {
            "modelID": "Optional_UniqueIDOfModel",
            "live2DItemFileName": "Optional_Live2DItemFileName",
        },
    )

    assert request.model_id == "Optional_UniqueIDOfModel"
    assert request.live2d_item_file_name == "Optional_Live2DItemFileName"


def test_trigger_request_emits_the_wire_shape() -> None:
    """Triggering a hotkey for the main model omits the item instance as an explicit null."""
    assert json.loads(
        HotkeyTriggerRequest(
            hotkey_id="HotkeyNameOrUniqueIdOfHotkeyToExecute"
        ).model_dump_json(),
    ) == {
        "hotkeyID": "HotkeyNameOrUniqueIdOfHotkeyToExecute",
        "itemInstanceID": None,
    }
    assert json.loads(
        HotkeyTriggerRequest(
            hotkey_id="HotkeyNameOrUniqueIdOfHotkeyToExecute",
            item_instance_id="Optional_ItemInstanceIdOfLive2DItem",
        ).model_dump_json(),
    ) == {
        "hotkeyID": "HotkeyNameOrUniqueIdOfHotkeyToExecute",
        "itemInstanceID": "Optional_ItemInstanceIdOfLive2DItem",
    }


def test_trigger_response_only_carries_the_hotkey_id() -> None:
    """The trigger response echoes the executed hotkey under its alias."""
    response = HotkeyTriggerResponse.model_validate(
        {"hotkeyID": "UniqueIdOfHotkeyThatWasExecuted"},
    )

    assert response.hotkey_id == "UniqueIdOfHotkeyThatWasExecuted"
    assert json.loads(response.model_dump_json()) == {
        "hotkeyID": "UniqueIdOfHotkeyThatWasExecuted",
    }
