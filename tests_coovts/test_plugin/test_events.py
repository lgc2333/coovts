"""Registering events, subscribing to them, and dispatching their frames to the handlers."""

import asyncio
from typing import TYPE_CHECKING

from coovts.errors import APIError
from coovts.plugin import PluginState, dispatch_handlers_inner
from coovts.subscriptions import EventRegistration
from coovts.types.api import MoveModelRequest, MoveModelResponse
from coovts.types.consts import ErrorID
from coovts.types.event import (
    ModelLoadedEventData,
    ModelMovedEventData,
    ModelOutlineEventConfig,
    ModelOutlineEventData,
)

from ..utils.async_helpers import finish, spin_until, tick
from ..utils.frames import envelope, real_frame, real_payload, sent_frame
from ..utils.plugin_fake import FakeTransport, install_transport
from ..utils.plugin_fixtures import handshake, make_plugin

if TYPE_CHECKING:
    import pytest


async def test_event_frame_reaches_matching_handler(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """An inbound event frame is decoded and delivered to the handler for its `messageType`."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    loaded: list[ModelLoadedEventData] = []
    moved: list[ModelMovedEventData] = []

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        loaded.append(data)

    @plugin.handle_event(ModelMovedEventData)
    async def on_moved(data: ModelMovedEventData) -> None:
        moved.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        # a frame captured from a real VTube Studio, VTS's own 32-hex request id included
        connection.feed(real_frame("ModelMovedEvent"))
        await spin_until(lambda: bool(moved), "model moved handler")
        assert len(moved) == 1
        assert moved[0].model_id == "6248f9ba0edc401c96de072a3350de3f"
        assert moved[0].model_position.size == -65.87860870361328
        assert loaded == []

        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(lambda: bool(loaded), "model loaded handler")
        assert len(loaded) == 1
        assert loaded[0].model_name == "model-a"
        assert loaded[0].model_id == "id-1"
        assert len(moved) == 1
    finally:
        await finish(plugin, run_task)


async def test_failing_handler_reports_and_recv_loop_survives(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A raising handler reaches `on_handler_run_failed` without stopping the receive loop."""
    from coovts.types.event import TestEventData

    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    failures: list[Exception] = []
    received: list[ModelLoadedEventData] = []

    @plugin.on_handler_run_failed
    async def on_failed(error: Exception) -> None:
        failures.append(error)

    @plugin.handle_event(TestEventData)
    async def on_test(data: TestEventData) -> None:
        raise RuntimeError(data.your_test_message)

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        received.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        connection.feed(
            envelope("TestEvent", {"yourTestMessage": "boom", "counter": 1})
        )
        await spin_until(lambda: bool(failures), "on_handler_run_failed")
        assert len(failures) == 1
        assert isinstance(failures[0], RuntimeError)
        assert str(failures[0]) == "boom"

        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(lambda: bool(received), "handler after a failure")
        assert len(received) == 1
    finally:
        await finish(plugin, run_task)


async def test_dispatch_without_failure_handlers_captures_the_failure() -> None:
    """A handler failure with no failure hook configured is captured, never raised."""

    async def explode() -> None:
        raise RuntimeError("boom")

    tasks = dispatch_handlers_inner([explode], None)
    assert tasks is not None

    results = await asyncio.gather(*tasks)
    assert isinstance(results[0], RuntimeError)


async def test_parked_handler_does_not_block_the_receive_loop(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A handler waiting on an event does not hold up the next request's answer."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    started = asyncio.Event()
    parked = asyncio.Event()

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        started.set()
        await parked.wait()

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(started.is_set, "handler parked on its event")

        call = asyncio.create_task(
            plugin.call_api(
                MoveModelRequest(time_in_seconds=1, values_are_relative_to_model=True),
            ),
        )
        await spin_until(
            lambda: len(connection.sent) >= 3, "call while a handler is parked"
        )

        request = sent_frame(connection, 2)
        connection.feed(envelope("MoveModelResponse", {}, request["requestID"]))

        response = await asyncio.wait_for(call, 1)
        assert isinstance(response, MoveModelResponse)
        assert not parked.is_set()
    finally:
        parked.set()
        await finish(plugin, run_task)


async def test_declared_event_is_subscribed_and_its_frames_reach_the_handler(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A declared event is subscribed to after authentication, and feeds the handler it carries."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    moved: list[ModelMovedEventData] = []

    @plugin.subscribe_event(ModelMovedEventData)
    async def on_moved(data: ModelMovedEventData) -> None:
        moved.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: len(connection.sent) >= 3, "subscription frame")

        request = sent_frame(connection, 2)
        assert request["messageType"] == "EventSubscriptionRequest"
        assert request["data"]["eventName"] == "ModelMovedEvent"
        assert request["data"]["subscribe"] is True
        assert request["data"]["config"] == {}

        connection.feed(real_frame("ModelMovedEvent"))
        await spin_until(lambda: bool(moved), "handler of the subscribed event")
        assert moved[0].model_id == "6248f9ba0edc401c96de072a3350de3f"
    finally:
        await finish(plugin, run_task)


async def test_declared_config_reaches_the_wire(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """The config a declaration was given is the one VTS receives with the subscription."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    plugin.subscribe_event(ModelOutlineEventData, ModelOutlineEventConfig(draw=True))

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: len(connection.sent) >= 3, "subscription frame")

        request = sent_frame(connection, 2)
        assert request["data"]["eventName"] == "ModelOutlineEvent"
        assert request["data"]["config"] == {"draw": True}
    finally:
        await finish(plugin, run_task)


async def test_awaited_declaration_subscribes_right_away(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """Awaiting a declaration sends it at once, and the declaration outlives the call."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        subscribing = asyncio.ensure_future(
            plugin.subscribe_event(ModelMovedEventData),
        )
        await spin_until(lambda: len(connection.sent) >= 3, "subscription frame")
        request = sent_frame(connection, 2)
        assert request["data"]["eventName"] == "ModelMovedEvent"

        connection.feed(
            envelope(
                "EventSubscriptionResponse",
                {"subscribedEventCount": 1, "subscribedEvents": ["ModelMovedEvent"]},
                request["requestID"],
            ),
        )
        response = await asyncio.wait_for(subscribing, 1)

        assert response.subscribed_events == ["ModelMovedEvent"]
        assert plugin.subscriptions.get("ModelMovedEvent") is not None
    finally:
        await finish(plugin, run_task)


async def test_declared_subscription_survives_a_reconnect(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A drop loses nothing: the declaration is subscribed to again on the new session."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(reconnect_delay=0)
    connection = transport.connection

    plugin.subscribe_event(ModelMovedEventData)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: len(connection.sent) >= 3, "first subscription")

        connection.drop()
        await spin_until(
            lambda: len(connection.sent) >= 4, "authentication after a reconnect"
        )
        auth_request = sent_frame(connection, 3)
        assert auth_request["messageType"] == "AuthenticationRequest"
        connection.feed(
            envelope(
                "AuthenticationResponse",
                {"authenticated": True, "reason": ""},
                auth_request["requestID"],
            ),
        )
        await spin_until(lambda: len(connection.sent) >= 5, "second subscription")

        resent = sent_frame(connection, 4)
        assert resent["messageType"] == "EventSubscriptionRequest"
        assert resent["data"]["eventName"] == "ModelMovedEvent"
        assert resent["data"]["subscribe"] is True
    finally:
        await finish(plugin, run_task)


async def test_refused_subscription_reaches_its_hook(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A subscription VTS refuses is reported to `on_subscribe_failed`, not raised."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    failures: list[tuple[EventRegistration, Exception]] = []

    @plugin.on_subscribe_failed
    async def on_failed(
        registration: EventRegistration,
        error: Exception,
    ) -> None:
        failures.append((registration, error))

    plugin.subscribe_event(ModelMovedEventData)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: len(connection.sent) >= 3, "subscription frame")

        request = sent_frame(connection, 2)
        connection.feed(
            envelope(
                "APIError",
                {
                    "errorID": ErrorID.EventSubscriptionRequestEventTypeUnknown,
                    "message": "Unknown API event type: ModelMovedEvent",
                },
                request["requestID"],
            ),
        )
        await spin_until(lambda: bool(failures), "on_subscribe_failed")

        registration, error = failures[0]
        assert registration.event_name == "ModelMovedEvent"
        assert isinstance(error, APIError)
        assert error.data.error_id == ErrorID.EventSubscriptionRequestEventTypeUnknown
        assert plugin.state is PluginState.AUTHENTICATED
    finally:
        await finish(plugin, run_task)


async def test_a_disposed_declaration_is_not_resubscribed(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """Disposing of a declaration cancels its subscription, and a reconnect does not bring it back."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(reconnect_delay=0)
    connection = transport.connection

    declared = plugin.subscribe_event(ModelMovedEventData)

    @declared
    async def on_moved(data: ModelMovedEventData) -> None:
        pass

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: len(connection.sent) >= 3, "subscription frame")

        disposing = asyncio.create_task(on_moved.dispose())
        await spin_until(lambda: len(connection.sent) >= 4, "cancellation frame")
        request = sent_frame(connection, 3)
        assert request["messageType"] == "EventSubscriptionRequest"
        assert request["data"]["eventName"] == "ModelMovedEvent"
        assert request["data"]["subscribe"] is False
        connection.feed(
            envelope(
                "EventSubscriptionResponse",
                {"subscribedEventCount": 0, "subscribedEvents": []},
                request["requestID"],
            ),
        )
        await asyncio.wait_for(disposing, 1)

        connection.drop()
        await spin_until(
            lambda: len(connection.sent) >= 5, "authentication after a reconnect"
        )
        auth_request = sent_frame(connection, 4)
        connection.feed(
            envelope(
                "AuthenticationResponse",
                {"authenticated": True, "reason": ""},
                auth_request["requestID"],
            ),
        )
        await spin_until(
            lambda: plugin.state is PluginState.AUTHENTICATED,
            "reauthentication",
        )
        await tick()

        assert len(connection.sent) == 5
    finally:
        await finish(plugin, run_task)


async def test_a_config_need_not_be_a_model(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A subscription sends the config it was given even when it is no model at all."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    plugin.subscribe_event(ModelOutlineEventData, {"draw": True})

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: len(connection.sent) >= 3, "subscription frame")

        assert sent_frame(connection, 2)["data"] == {
            "eventName": "ModelOutlineEvent",
            "subscribe": True,
            "config": {"draw": True},
        }
    finally:
        await finish(plugin, run_task)


async def test_an_event_named_by_its_wire_name_gets_the_raw_payload(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A handler registered by event name receives the payload as it arrived, undecoded."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    payloads: list[object] = []

    @plugin.handle_event("ModelMovedEvent")
    async def on_moved(data: object) -> None:
        payloads.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        connection.feed(real_frame("ModelMovedEvent"))
        await spin_until(lambda: bool(payloads), "handler registered by name")

        assert payloads == [real_payload("ModelMovedEvent")]
    finally:
        await finish(plugin, run_task)


async def test_subscribing_by_event_name_sends_the_config_it_was_given(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """An event named by its wire name is subscribed to with exactly the config it was given."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    plugin.subscribe_event(
        "ModelOutlineEvent",
        ModelOutlineEventConfig(draw=True),
    )

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: len(connection.sent) >= 3, "subscription frame")

        assert sent_frame(connection, 2)["data"] == {
            "eventName": "ModelOutlineEvent",
            "subscribe": True,
            "config": {"draw": True},
        }
    finally:
        await finish(plugin, run_task)


async def test_handle_event_alone_subscribes_to_nothing(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """`handle_event` stays local: it attaches a handler and sends nothing to VTS."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    @plugin.handle_event(ModelMovedEventData)
    async def on_moved(data: ModelMovedEventData) -> None:
        pass

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await tick()

        assert len(connection.sent) == 2
    finally:
        await finish(plugin, run_task)


async def test_a_disposed_local_handler_stops_dispatching(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A handler registered without a subscription can dispose of itself, sending no frame."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    moved: list[ModelMovedEventData] = []

    @plugin.handle_event(ModelMovedEventData)
    async def on_moved(data: ModelMovedEventData) -> None:
        moved.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        connection.feed(real_frame("ModelMovedEvent"))
        await spin_until(lambda: bool(moved), "local handler")

        assert await on_moved.dispose() is None

        connection.feed(real_frame("ModelMovedEvent"))
        await tick()

        assert len(moved) == 1
        assert len(connection.sent) == 2
    finally:
        await finish(plugin, run_task)
