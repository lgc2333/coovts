"""Namespace-wide invariants over the `coovts.types.api` and `coovts.types.event` models,
and the decode of frames a real VTube Studio sent."""

import json

import pytest
from pydantic import BaseModel, ValidationError

from coovts.types import api, event
from coovts.types.shared import (
    BaseResponse,
    get_api_response_model,
    get_event_name,
    get_message_type,
)

from ..utils.frames import real_error_frame, real_payload


def test_every_api_request_resolves_to_its_response_sibling() -> None:
    """Each `*Request` in the api namespace is a model resolving to its `*Response` sibling."""
    request_names = [name for name in vars(api) if name.endswith("Request")]
    assert "MoveModelRequest" in request_names

    for name in request_names:
        model = getattr(api, name)
        assert isinstance(model, type), f"{name} is not a class"
        assert issubclass(model, BaseModel), f"{name} is not a pydantic model"
        assert get_message_type(model) == name

        response = get_api_response_model(model)
        assert issubclass(response, BaseModel), f"{name} resolves to a non-model"
        assert getattr(api, response.__name__, None) is response

        has_escape_hatch = bool(
            getattr(model, "resp_t", None) or getattr(model, "resp_m", None),
        )
        if not has_escape_hatch:
            assert response.__name__ == name.removesuffix("Request") + "Response"


def test_every_event_data_model_agrees_with_its_config_sibling() -> None:
    """Each `*EventData` in the event namespace names an `*Event` its config sibling shares."""
    data_names = [name for name in vars(event) if name.endswith("EventData")]
    config_names = [name for name in vars(event) if name.endswith("EventConfig")]
    assert "ModelLoadedEventData" in data_names
    assert "ModelLoadedEventConfig" in config_names

    for name in data_names:
        data_model = getattr(event, name)
        assert isinstance(data_model, type), f"{name} is not a class"
        assert issubclass(data_model, BaseModel), f"{name} is not a pydantic model"

        event_name = get_event_name(data_model)
        assert event_name.endswith("Event"), f"{name} names {event_name}"

        config_model = getattr(event, name.removesuffix("EventData") + "EventConfig")
        assert issubclass(config_model, BaseModel), f"{name} has no config model"
        assert get_event_name(config_model) == event_name


def test_request_serializes_by_alias_but_rejects_alias_input() -> None:
    """`ModelLoadRequest` emits camelCase, yet refuses to be built from the wire alias."""
    request = api.ModelLoadRequest(model_id="m1")
    assert request.model_id == "m1"

    payload: dict[str, str] = json.loads(request.model_dump_json())
    assert payload["modelID"] == "m1"
    assert "model_id" not in payload

    with pytest.raises(ValidationError) as excinfo:
        api.ModelLoadRequest.model_validate({"modelID": "m1"})

    assert [error["loc"] for error in excinfo.value.errors()] == [("model_id",)]
    assert "model_id" in str(excinfo.value)


def test_response_model_validates_by_wire_alias_only() -> None:
    """`ModelLoadResponse` decodes the wire spelling and ignores the python field name."""
    response = api.ModelLoadResponse.model_validate({"modelID": "m1"})
    assert response.model_id == "m1"

    with pytest.raises(ValidationError) as excinfo:
        api.ModelLoadResponse.model_validate({"model_id": "m1"})

    assert [error["loc"] for error in excinfo.value.errors()] == [("modelID",)]
    assert "modelID" in str(excinfo.value)


def test_response_model_ignores_unknown_wire_fields() -> None:
    """A response payload carrying a field this library does not know still decodes."""
    response = api.ModelLoadResponse.model_validate(
        {"modelID": "m1", "someFieldVtsAddedLater": 1},
    )

    assert response.model_id == "m1"


def test_real_response_frames_decode() -> None:
    """Responses a real VTube Studio sent decode, shared position model included."""
    current = api.CurrentModelResponse.model_validate(
        real_payload("CurrentModelResponse"),
    )
    assert current.model_name == "饼干寻"
    assert current.number_of_live2d_parameters == 50
    assert current.model_position.rotation == 358.4307861328125
    assert current.model_position.size == -65.87860870361328

    state = api.APIStateResponse.model_validate(real_payload("APIStateResponse"))
    assert state.v_tube_studio_version == "1.35.10"
    assert state.current_session_authenticated is True


def test_real_error_frames_decode_with_their_ids() -> None:
    """The `APIError` frames a real VTube Studio sent decode into `APIErrorResponse`."""
    expectations = {
        7: "Unknown messageType: ArtMeshAtPositionRequest",
        50: "User denied authentication request for your plugin.",
        51: (
            "Cannot start authentication process because authentication is currently ongoing."
            " Authentication request window is open in VTube Studio."
        ),
        1250: "No item with the given item instance ID is currently loaded.",
    }

    for error_id, message in expectations.items():
        envelope = BaseResponse.model_validate_json(real_error_frame(error_id))
        assert envelope.message_type == "APIError"
        error = api.APIErrorResponse.model_validate(envelope.data)
        assert (error.error_id, error.message) == (error_id, message)
