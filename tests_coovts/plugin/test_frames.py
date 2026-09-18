"""Inbound frames that are malformed, unknown, or carry unmodelled fields."""

import asyncio
from typing import TYPE_CHECKING

from coovts.plugin import PluginState
from coovts.types.api import APIStateRequest, APIStateResponse
from coovts.types.event import ModelLoadedEventData

from ..utils.async_helpers import finish, spin_until
from ..utils.frames import envelope, real_payload, sent_frame
from ..utils.plugin_fake import FakeTransport, install_transport
from ..utils.plugin_fixtures import handshake, make_plugin

if TYPE_CHECKING:
    import pytest


async def test_unparseable_frame_reaches_parse_error_hook(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A frame that is not a valid envelope is reported to `on_parse_data_error`."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    errors: list[tuple[str | bytes, Exception]] = []
    received: list[ModelLoadedEventData] = []

    @plugin.on_parse_data_error
    async def on_error(raw: str | bytes, error: Exception) -> None:
        errors.append((raw, error))

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        received.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        connection.feed("{not json")
        await spin_until(lambda: bool(errors), "on_parse_data_error")
        assert len(errors) == 1
        assert errors[0][0] == "{not json"
        assert isinstance(errors[0][1], ValueError)

        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(lambda: bool(received), "receive loop after a parse error")
        assert len(received) == 1
    finally:
        await finish(plugin, run_task)


async def test_unknown_message_type_is_dropped(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A well-formed frame with an unknown `messageType` is ignored, not treated as an error."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    errors: list[tuple[str | bytes, Exception]] = []
    received: list[ModelLoadedEventData] = []

    @plugin.on_parse_data_error
    async def on_error(raw: str | bytes, error: Exception) -> None:
        errors.append((raw, error))

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        received.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        connection.feed(envelope("SomeFutureEvent", {"anything": 1}, "4242"))
        connection.feed(envelope("AnotherUnknownEvent", {}))
        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(lambda: bool(received), "receive loop after unknown frames")

        assert errors == []
        assert plugin.state is PluginState.AUTHENTICATED
    finally:
        await finish(plugin, run_task)


async def test_invalid_event_payload_reaches_parse_error_hook(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """An event whose payload does not decode is reported instead of being dispatched."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    errors: list[tuple[str | bytes, Exception]] = []
    received: list[ModelLoadedEventData] = []

    @plugin.on_parse_data_error
    async def on_error(raw: str | bytes, error: Exception) -> None:
        errors.append((raw, error))

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        received.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        frame = envelope("ModelLoadedEvent", {"modelLoaded": True})
        connection.feed(frame)
        await spin_until(lambda: bool(errors), "on_parse_data_error for a bad payload")

        assert [raw for raw, _ in errors] == [frame]
        assert received == []
    finally:
        await finish(plugin, run_task)


async def test_unknown_payload_fields_are_ignored(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A payload carrying a field the library does not model still decodes (ADR-0003)."""
    from coovts.types.event import TestEventData

    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    received: list[TestEventData] = []

    @plugin.handle_event(TestEventData)
    async def on_test(data: TestEventData) -> None:
        received.append(data)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        # a payload captured from a real VTube Studio, plus a field a future VTS could add
        connection.feed(
            envelope(
                "TestEvent",
                {**real_payload("TestEvent"), "someFieldVtsAddedLater": {"nested": 1}},
            ),
        )
        await spin_until(
            lambda: bool(received), "handler for a payload with extra fields"
        )
        assert received[0].counter == 560

        call = asyncio.create_task(plugin.call_api(APIStateRequest()))
        await spin_until(lambda: len(connection.sent) >= 3, "api state request")

        request = sent_frame(connection, 2)
        connection.feed(
            envelope(
                "APIStateResponse",
                {**real_payload("APIStateResponse"), "futureField": 1},
                request["requestID"],
            ),
        )
        response = await asyncio.wait_for(call, 1)
        assert isinstance(response, APIStateResponse)
        assert response.vtube_studio_version == "1.35.10"
    finally:
        await finish(plugin, run_task)
