"""Wire-shape tests for the expression models of `coovts.types.api`."""

import json

from coovts.types.api import (
    ExpressionActivationRequest,
    ExpressionActivationResponse,
    ExpressionInfo,
    ExpressionStateRequest,
    ExpressionStateResponse,
)


def test_documented_state_response_decodes() -> None:
    """The documented expression state response decodes into the model tree."""
    response = ExpressionStateResponse.model_validate(
        {
            "modelLoaded": True,
            "modelName": "My Currently Loaded Model",
            "modelID": "UniqueIDOfModel",
            "expressions": [
                {
                    "name": "myExpression_optional_1",
                    "file": "myExpression_optional_1 .exp3.json",
                    "active": False,
                    "deactivateWhenKeyIsLetGo": False,
                    "autoDeactivateAfterSeconds": False,
                    "secondsRemaining": 0,
                    "usedInHotkeys": [
                        {
                            "name": "Some Hotkey",
                            "id": "SomeUniqueIdToIdentifyHotkeyWith1",
                        },
                        {
                            "name": "Some other Hotkey",
                            "id": "SomeUniqueIdToIdentifyHotkeyWith2",
                        },
                    ],
                    "parameters": [{"name": "SomeLive2DParamID", "value": 0}],
                },
            ],
        },
    )

    assert response.model_loaded is True
    assert response.model_name == "My Currently Loaded Model"
    assert response.model_id == "UniqueIDOfModel"

    expression = response.expressions[0]
    assert expression.name == "myExpression_optional_1"
    assert expression.file == "myExpression_optional_1 .exp3.json"
    assert expression.active is False
    assert expression.deactivate_when_key_is_let_go is False
    assert expression.auto_deactivate_after_seconds is False
    assert expression.seconds_remaining == 0.0
    assert [(hotkey.name, hotkey.id) for hotkey in expression.used_in_hotkeys] == [
        ("Some Hotkey", "SomeUniqueIdToIdentifyHotkeyWith1"),
        ("Some other Hotkey", "SomeUniqueIdToIdentifyHotkeyWith2"),
    ]
    assert [(param.name, param.value) for param in expression.parameters] == [
        ("SomeLive2DParamID", 0.0),
    ]


def test_expression_info_defaults_seconds_since_last_active() -> None:
    """A response without `secondsSinceLastActive` defaults it to zero and still emits it."""
    info = ExpressionInfo.model_validate(
        {
            "name": "myExpression_optional_1",
            "file": "myExpression_optional_1.exp3.json",
            "active": False,
            "deactivateWhenKeyIsLetGo": False,
            "autoDeactivateAfterSeconds": False,
            "secondsRemaining": 0,
        },
    )

    assert info.seconds_since_last_active == 0.0
    assert info.used_in_hotkeys == []
    assert info.parameters == []
    assert json.loads(info.model_dump_json())["secondsSinceLastActive"] == 0.0


def test_expression_info_round_trips_seconds_since_last_active() -> None:
    """A wire `secondsSinceLastActive` value is read and re-emitted under its alias."""
    info = ExpressionInfo.model_validate(
        {
            "name": "myExpression_optional_1",
            "file": "myExpression_optional_1.exp3.json",
            "active": True,
            "deactivateWhenKeyIsLetGo": True,
            "autoDeactivateAfterSeconds": True,
            "secondsRemaining": 5.0,
            "secondsSinceLastActive": 12.5,
        },
    )

    assert info.seconds_since_last_active == 12.5
    assert json.loads(info.model_dump_json())["secondsSinceLastActive"] == 12.5


def test_state_request_defaults_dump_the_wire_shape() -> None:
    """A bare state request asks for details across all expressions."""
    assert json.loads(ExpressionStateRequest().model_dump_json()) == {
        "details": True,
        "expressionFile": None,
    }


def test_state_request_round_trips_through_wire_keys() -> None:
    """An explicit single-expression state request survives a wire round trip."""
    wire = {"details": False, "expressionFile": "myExpression_1.exp3.json"}

    assert (
        json.loads(
            ExpressionStateRequest.model_validate(wire).model_dump_json(),
        )
        == wire
    )


def test_activation_request_defaults_dump_the_wire_shape() -> None:
    """Building an activation request from field names emits the alias keys and fade default."""
    request = ExpressionActivationRequest(
        expression_file="myExpression_1.exp3.json",
        active=True,
    )

    assert json.loads(request.model_dump_json()) == {
        "expressionFile": "myExpression_1.exp3.json",
        "fadeTime": 0.25,
        "active": True,
    }
    assert json.loads(ExpressionActivationResponse().model_dump_json()) == {}
