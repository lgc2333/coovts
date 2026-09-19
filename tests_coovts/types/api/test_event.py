"""Wire-shape tests for the event models of `coovts.types.api`."""

import json

import pytest
from pydantic import ValidationError

from coovts.types.api import EventSubscriptionRequest, EventSubscriptionResponse


def test_documented_subscription_response_decodes() -> None:
    """The example subscription response decodes into the response model."""
    response = EventSubscriptionResponse.model_validate(
        {
            "subscribedEventCount": 2,
            "subscribedEvents": ["TestEvent", "ModelLoadedEvent"],
        },
    )

    assert response.subscribed_event_count == 2
    assert response.subscribed_events == ["TestEvent", "ModelLoadedEvent"]


def test_subscription_request_dumps_the_wire_shape() -> None:
    """Building from python field names emits the camelCase aliases."""
    request = EventSubscriptionRequest(
        event_name="ModelLoadedEvent",
        subscribe=True,
        config={},
    )

    assert json.loads(request.model_dump_json()) == {
        "eventName": "ModelLoadedEvent",
        "subscribe": True,
        "config": {},
    }


def test_subscription_request_carries_the_event_config() -> None:
    """The free-form config object passes through with the event specific keys intact."""
    request = EventSubscriptionRequest.model_validate(
        {
            "eventName": "TestEvent",
            "subscribe": True,
            "config": {"testMessageForEvent": "text the event will return"},
        },
    )

    assert request.event_name == "TestEvent"
    assert json.loads(request.model_dump_json())["config"] == {
        "testMessageForEvent": "text the event will return",
    }


def test_unsubscribe_all_request_emits_the_wire_shape() -> None:
    """Unsubscribing everything names no event and carries no config, both stated on purpose."""
    request = EventSubscriptionRequest(event_name=None, config=None, subscribe=False)

    assert json.loads(request.model_dump_json()) == {
        "eventName": None,
        "subscribe": False,
        "config": None,
    }


def test_subscription_request_still_needs_every_field() -> None:
    """Neither field defaults, so unsubscribing everything cannot happen by omission.

    A frame that leaves one of them out is rejected, and the constructor makes the omission
    impossible to write in the first place.
    """
    with pytest.raises(ValidationError):
        EventSubscriptionRequest.model_validate({"subscribe": False, "config": None})

    with pytest.raises(ValidationError):
        EventSubscriptionRequest.model_validate({"subscribe": False, "eventName": None})


def test_unsubscribe_request_round_trips_through_wire_keys() -> None:
    """An unsubscribe payload survives a wire-key round trip unchanged."""
    wire = {"eventName": "ModelLoadedEvent", "subscribe": False, "config": {}}

    assert (
        json.loads(
            EventSubscriptionRequest.model_validate(wire).model_dump_json(),
        )
        == wire
    )
