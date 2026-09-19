"""Wire-shape tests for the error models of `coovts.types.api`."""

import json

from coovts.types.api import APIErrorResponse


def test_documented_error_payload_decodes() -> None:
    """The access-denied error from the reference docs decodes into the response model."""
    response = APIErrorResponse.model_validate(
        {
            "errorID": 50,
            "message": "User has denied API access for your plugin.",
        },
    )

    assert response.error_id == 50
    assert response.message == "User has denied API access for your plugin."


def test_unknown_message_type_error_decodes() -> None:
    """The error id alias maps onto the python `error_id` field for any error code."""
    response = APIErrorResponse.model_validate(
        {
            "errorID": 7,
            "message": "Unknown messageType: Foo",
        },
    )

    assert response.error_id == 7
    assert response.message == "Unknown messageType: Foo"


def test_error_response_dumps_the_wire_shape() -> None:
    """Dumping the model emits exactly the alias keys VTube Studio sends."""
    response = APIErrorResponse.model_validate(
        {
            "errorID": 7,
            "message": "Unknown messageType: Foo",
        },
    )

    assert json.loads(response.model_dump_json()) == {
        "errorID": 7,
        "message": "Unknown messageType: Foo",
    }


def test_error_response_round_trips_through_wire_keys() -> None:
    """A wire-key dict survives a validate/dump round trip unchanged."""
    wire = {"errorID": -1, "message": ""}

    assert json.loads(APIErrorResponse.model_validate(wire).model_dump_json()) == wire
