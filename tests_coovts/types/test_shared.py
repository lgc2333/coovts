"""Unit tests for the wire-name resolvers in `coovts.types.shared`."""

from typing import ClassVar

import pytest
from pydantic import BaseModel

from coovts.types import api, event
from coovts.types.shared import (
    get_api_response_model,
    get_event_name,
    get_message_type,
)


def test_message_type_is_class_name_verbatim() -> None:
    """The message type is the class name, for a model class and for an instance."""
    assert get_message_type(api.ModelLoadRequest) == "ModelLoadRequest"

    instance = api.ModelLoadRequest(model_id="m1")
    assert get_message_type(instance) == "ModelLoadRequest"


def test_response_model_swaps_request_suffix() -> None:
    """A `XRequest` model resolves to `XResponse`, from the class and from an instance."""
    assert get_api_response_model(api.ModelLoadRequest) is api.ModelLoadResponse

    instance = api.ModelLoadRequest(model_id="m1")
    assert get_api_response_model(instance) is api.ModelLoadResponse


def test_event_data_and_config_agree_on_event_name() -> None:
    """An `EventData` model and its `EventConfig` sibling name the same event."""
    data_name = get_event_name(event.ModelLoadedEventData)
    assert data_name == "ModelLoadedEvent"

    config = event.ModelLoadedEventConfig.model_validate({})
    assert get_event_name(event.ModelLoadedEventConfig) == data_name
    assert get_event_name(config) == data_name


def test_msg_t_overrides_message_type() -> None:
    """An explicit `msg_t` replaces the class name as the wire message type."""

    class RenamedRequest(BaseModel):
        msg_t: ClassVar[str] = "CustomMessage"

    assert get_message_type(RenamedRequest) == "CustomMessage"
    assert get_message_type(RenamedRequest) != RenamedRequest.__name__


def test_msg_t_overrides_event_name() -> None:
    """An explicit `msg_t` names the event of a model the suffix rule cannot name."""

    class UnconventionalEvent(BaseModel):
        msg_t: ClassVar[str] = "CustomEventMessage"

    assert get_event_name(UnconventionalEvent) == "CustomEventMessage"


def test_resp_t_overrides_response_convention() -> None:
    """A `resp_t` string resolves the response of a model the `Request` swap cannot name."""

    class ModelLoadQuery(BaseModel):
        resp_t: ClassVar[str] = "ModelLoadResponse"

    assert get_api_response_model(ModelLoadQuery) is api.ModelLoadResponse


def test_resp_m_overrides_response_convention() -> None:
    """A `resp_m` model wins over the `Request`/`Response` swap that would resolve."""

    class ModelLoadRequest(BaseModel):
        resp_m: ClassVar[type[BaseModel]] = api.MoveModelResponse

    assert get_api_response_model(ModelLoadRequest) is api.MoveModelResponse


def test_resp_m_takes_precedence_over_unresolvable_resp_t() -> None:
    """With both escape hatches set, a bogus `resp_t` never displaces the `resp_m` model."""

    class AwkwardQuery(BaseModel):
        resp_t: ClassVar[str] = "NoSuchResponse"
        resp_m: ClassVar[type[BaseModel]] = api.MoveModelResponse

    assert get_api_response_model(AwkwardQuery) is api.MoveModelResponse


def test_unresolvable_response_raises_value_error() -> None:
    """A model whose name the convention cannot resolve fails with `ValueError`."""

    class NotARequest(BaseModel):
        """Ends in neither `Request` nor any resolvable name."""

    class GhostRequest(BaseModel):
        """Ends in `Request`, but `GhostResponse` is not in `coovts.types.api`."""

    class PurelyLocal(BaseModel):
        """Ends in no `Request` suffix and carries no escape hatch."""

    with pytest.raises(ValueError):  # noqa: PT011
        get_api_response_model(NotARequest)

    with pytest.raises(ValueError):  # noqa: PT011
        get_api_response_model(GhostRequest)

    with pytest.raises(ValueError):  # noqa: PT011
        get_api_response_model(PurelyLocal)


def test_resp_t_target_missing_from_api_raises_value_error() -> None:
    """A `resp_t` naming a model absent from `coovts.types.api` fails with `ValueError`."""

    class MissingTargetRequest(BaseModel):
        resp_t: ClassVar[str] = "NoSuchResponseModel"

    with pytest.raises(ValueError):  # noqa: PT011
        get_api_response_model(MissingTargetRequest)


def test_unresolvable_event_name_raises_value_error() -> None:
    """A model the event suffix rule cannot name and that carries no `msg_t` raises."""

    class NotAnEvent(BaseModel):
        """Ends in neither `EventData` nor `EventConfig`, and sets no `msg_t`."""

    with pytest.raises(ValueError):  # noqa: PT011
        get_event_name(NotAnEvent)


def test_non_string_msg_t_raises_type_error() -> None:
    """A `msg_t` that is not a `str` fails both name resolvers with `TypeError`."""

    class BadMsgTypeRequest(BaseModel):
        msg_t: ClassVar[int] = 1

    with pytest.raises(TypeError):
        get_message_type(BadMsgTypeRequest)

    with pytest.raises(TypeError):
        get_event_name(BadMsgTypeRequest)


def test_non_string_resp_t_raises_type_error() -> None:
    """A `resp_t` that is not a `str` fails with `TypeError`."""

    class BadRespTypeRequest(BaseModel):
        resp_t: ClassVar[int] = 1

    with pytest.raises(TypeError):
        get_api_response_model(BadRespTypeRequest)


def test_non_model_resp_m_raises_type_error() -> None:
    """A `resp_m` that is not a `BaseModel` subclass fails with `TypeError`."""

    class BadRespModelRequest(BaseModel):
        resp_m: ClassVar[type] = int

    with pytest.raises(TypeError):
        get_api_response_model(BadRespModelRequest)
