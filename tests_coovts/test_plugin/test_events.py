"""Dispatching inbound events to the handlers registered for them."""

import asyncio
from typing import TYPE_CHECKING

from coovts.plugin import dispatch_handlers_inner
from coovts.types.api import MoveModelRequest, MoveModelResponse
from coovts.types.event import ModelLoadedEventData, ModelMovedEventData

from ..utils.async_helpers import finish, spin_until
from ..utils.frames import envelope, real_frame, sent_frame
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
