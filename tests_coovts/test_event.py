"""The registry of registered events, and the subscriptions it sends for them."""

from typing import ClassVar

import pytest

from coovts.errors import NetworkError
from coovts.event import EventSubscriptionRegistry, default_event_config
from coovts.types import VTSBaseModel, event
from coovts.types.api import EventSubscriptionRequest, EventSubscriptionResponse


def make_registry() -> tuple[EventSubscriptionRegistry, list[EventSubscriptionRequest]]:
    """A registry whose frames are recorded instead of going to VTube Studio."""
    sent: list[EventSubscriptionRequest] = []

    async def send(request: EventSubscriptionRequest) -> EventSubscriptionResponse:
        sent.append(request)
        return EventSubscriptionResponse(
            subscribed_event_count=1,
            subscribed_events=[request.event_name],
        )

    return EventSubscriptionRegistry(send), sent


MOVED = event.ModelMovedEventData(
    model_id="model-id",
    model_name="model-a",
    model_position=event.ModelPosition(
        position_x=0.0,
        position_y=0.0,
        rotation=0.0,
        size=1.0,
    ),
)


def test_registration_by_event_name_keeps_no_model() -> None:
    """Naming an event by its wire name registers it without a data model to decode with."""
    registry, _ = make_registry()

    registration = registry.registration("ModelMovedEvent")

    assert registration.event_name == "ModelMovedEvent"
    assert registration.data_model is None


def test_subscribing_by_event_name_records_the_config_it_was_given() -> None:
    """A named event subscribes with the config handed to it, since no model can supply one."""
    registry, _ = make_registry()
    config = event.ModelMovedEventConfig()

    registration = registry.subscribe("ModelMovedEvent", config)

    assert registration.config is config


def test_subscribing_by_event_name_without_a_config_sends_an_empty_one() -> None:
    """A named event has no config model to build from, so an empty config is what goes out."""
    registry, _ = make_registry()

    registration = registry.subscribe("ModelMovedEvent")

    assert registration.config == {}


def test_default_event_config_builds_the_config_of_an_event() -> None:
    """The config of an event that requires no field is built from its defaults."""
    assert (
        default_event_config(event.ModelMovedEventData) == event.ModelMovedEventConfig()
    )


def test_default_event_config_refuses_when_a_field_is_required() -> None:
    """A config with a required field cannot be defaulted, and names the field it needs."""
    with pytest.raises(ValueError, match="tracking_points"):
        default_event_config(event.ArtMeshTrackingEventData)


def test_registration_reuses_the_record_kept_for_an_event() -> None:
    """Two registrations of one event share a record, so its handlers and config stay together."""
    registry, _ = make_registry()
    declared = registry.subscribe(
        event.ModelMovedEventData, event.ModelMovedEventConfig()
    )

    again = registry.registration(event.ModelMovedEventData)

    assert again is declared
    assert again.config is declared.config
    assert registry.get("ModelMovedEvent") is declared


async def test_decorating_hands_back_the_handler_with_dispose() -> None:
    """The decorated handler is callable as it was, and disposes of the event it was declared for."""
    registry, sent = make_registry()
    seen: list[event.ModelMovedEventData] = []

    @registry.subscribe(event.ModelMovedEventData)
    async def on_moved(data: event.ModelMovedEventData) -> None:
        seen.append(data)

    await on_moved(MOVED)

    assert seen == [MOVED]

    await on_moved.dispose()

    assert [(request.event_name, request.subscribe) for request in sent] == [
        ("ModelMovedEvent", False),
    ]
    assert registry.get("ModelMovedEvent") is None


def test_a_later_registration_does_not_drop_the_config() -> None:
    """Adding a handler to a subscribed event leaves the subscription it was given alone."""
    registry, _ = make_registry()
    config = event.ModelMovedEventConfig()
    registry.subscribe(event.ModelMovedEventData, config)

    registry.registration(event.ModelMovedEventData)

    registration = registry.get("ModelMovedEvent")
    assert registration is not None
    assert registration.config is config


async def test_dispose_cancels_the_subscription_and_forgets_the_event() -> None:
    """Disposing of a registration sends `subscribe: false` and takes it out of the registry."""
    registry, sent = make_registry()
    config = event.ModelOutlineEventConfig(draw=True)

    @registry.subscribe(event.ModelOutlineEventData, config)
    async def on_outline(data: event.ModelOutlineEventData) -> None:
        pass

    registration = registry.get("ModelOutlineEvent")
    assert registration is not None
    response = await registration.dispose()

    assert response is not None
    assert [(request.event_name, request.subscribe) for request in sent] == [
        ("ModelOutlineEvent", False),
    ]
    assert sent[0].config is config
    assert registry.get("ModelOutlineEvent") is None
    assert list(registry) == []


async def test_disposing_twice_sends_one_frame() -> None:
    """A registration that is already gone does not send a second cancellation."""
    registry, sent = make_registry()
    registration = registry.subscribe(event.ModelMovedEventData)

    await registration.dispose()
    again = await registration.dispose()

    assert again is None
    assert len(sent) == 1


async def test_dispose_of_a_handler_only_registration_sends_nothing() -> None:
    """A registration with no config has no subscription to cancel, and is dropped anyway."""
    registry, sent = make_registry()
    registration = registry.registration(event.ModelMovedEventData)

    assert await registration.dispose() is None

    assert sent == []
    assert registry.get("ModelMovedEvent") is None


async def test_dispose_offline_forgets_the_event_without_failing() -> None:
    """With no connection there is no subscription to cancel, so only the registration goes."""

    async def no_connection(
        request: EventSubscriptionRequest,
    ) -> EventSubscriptionResponse:
        raise NetworkError("Not connected to VTube Studio")

    registry = EventSubscriptionRegistry(no_connection)
    registration = registry.subscribe(event.ModelMovedEventData)

    assert await registry.dispose(registration) is None

    assert registry.get("ModelMovedEvent") is None


async def test_send_refuses_a_registration_that_carries_no_config() -> None:
    """A handler-only registration has nothing to subscribe with, so sending it fails."""
    registry, _ = make_registry()
    registration = registry.registration(event.ModelMovedEventData)

    with pytest.raises(ValueError, match="no config"):
        await registry.send(registration)


async def test_send_refuses_a_disposed_registration() -> None:
    """A registration that was given up cannot be sent again."""
    registry, _ = make_registry()
    registration = registry.subscribe(event.ModelMovedEventData)
    await registration.dispose()

    with pytest.raises(ValueError, match="not live"):
        await registry.send(registration)


async def test_walking_the_registry_survives_a_dispose_inside_the_walk() -> None:
    """The walk runs over a snapshot, so giving a registration up inside it does not break."""
    registry, _ = make_registry()
    registry.subscribe(event.ModelMovedEventData)
    registry.subscribe(event.ModelLoadedEventData)
    walked: list[str] = []

    for registration in registry:
        walked.append(registration.event_name)
        await registration.dispose()

    assert walked == ["ModelMovedEvent", "ModelLoadedEvent"]
    assert list(registry) == []


class AliasedMovedEvent(VTSBaseModel):
    """A model that names `ModelMovedEvent` too, through the `msg_t` escape hatch."""

    msg_t: ClassVar[str] = "ModelMovedEvent"


def test_a_model_named_after_the_event_upgrades_the_registration() -> None:
    """Declaring an event by name first does not cost the model declared after it."""
    registry, _ = make_registry()

    registration = registry.registration("ModelMovedEvent")
    same = registry.registration(event.ModelMovedEventData)

    assert same is registration
    assert registration.data_model is event.ModelMovedEventData


def test_a_model_arriving_late_still_brings_its_default_config() -> None:
    """The default config a name cannot supply is built once the model arrives."""
    registry, _ = make_registry()

    registry.subscribe("ModelOutlineEvent")
    registration = registry.subscribe(event.ModelOutlineEventData)

    assert registration.config == default_event_config(event.ModelOutlineEventData)


def test_two_models_naming_one_event_are_refused() -> None:
    """Two models cannot decode one event name, so the second one is refused."""
    registry, _ = make_registry()
    registry.registration(event.ModelMovedEventData)

    with pytest.raises(ValueError, match="ModelMovedEvent"):
        registry.registration(AliasedMovedEvent)


def test_a_model_arriving_after_a_named_subscription_replaces_its_empty_config() -> (
    None
):
    """Completing a named declaration with a model sends that model's defaults, not `{}`."""
    registry, _ = make_registry()
    registry.subscribe("ModelOutlineEvent")

    registration = registry.registration(event.ModelOutlineEventData)

    assert registration.data_model is event.ModelOutlineEventData
    assert registration.config == default_event_config(event.ModelOutlineEventData)


def test_a_config_a_caller_passed_survives_a_late_model() -> None:
    """A model completing a named declaration leaves a config the caller chose alone."""
    registry, _ = make_registry()
    config = {"hand": "picked"}
    registry.subscribe("ModelOutlineEvent", config)

    registration = registry.registration(event.ModelOutlineEventData)

    assert registration.config == config


def test_a_late_model_with_a_required_config_field_is_refused() -> None:
    """A model whose config cannot be defaulted raises where the name alone could not."""
    registry, _ = make_registry()
    registry.subscribe("ArtMeshTrackingEvent")

    with pytest.raises(ValueError, match="tracking_points"):
        registry.registration(event.ArtMeshTrackingEventData)
