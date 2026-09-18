"""`call_api`: request/response correlation, timeouts, cancellation and send errors."""

import asyncio
from typing import TYPE_CHECKING, cast

import pytest
from websockets.exceptions import ConnectionClosedError

from coovts.errors import NetworkError, RequestTimeout
from coovts.plugin import PluginState
from coovts.types.api import MoveModelRequest, MoveModelResponse
from coovts.types.event import ModelLoadedEventData

from ..utils.async_helpers import finish, spin_until
from ..utils.frames import envelope, sent_frame
from ..utils.plugin_fake import FakeTransport, install_transport
from ..utils.plugin_fixtures import handshake, make_plugin

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


async def test_call_api_resolves_only_the_matching_request_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An in-flight call is resolved by the response echoing its `requestID`, and no other."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        call = asyncio.create_task(
            plugin.call_api(
                MoveModelRequest(time_in_seconds=1, values_are_relative_to_model=True),
            ),
        )
        await spin_until(lambda: len(connection.sent) >= 3, "move model request")

        request = sent_frame(connection, 2)
        assert request["messageType"] == "MoveModelRequest"
        assert request["requestID"] is not None
        assert request["requestID"].isdigit()
        assert len({sent_frame(connection, i)["requestID"] for i in range(3)}) == 3

        sentinel: list[ModelLoadedEventData] = []

        @plugin.handle_event(ModelLoadedEventData)
        async def on_loaded(data: ModelLoadedEventData) -> None:
            sentinel.append(data)

        connection.feed(envelope("MoveModelResponse", {}, "999999"))
        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(
            lambda: bool(sentinel), "sentinel frame after the mismatched one"
        )
        assert not call.done()

        connection.feed(envelope("MoveModelResponse", {}, request["requestID"]))
        response = await asyncio.wait_for(call, 1)
        assert isinstance(response, MoveModelResponse)
    finally:
        await finish(plugin, run_task)


async def test_connection_drop_fails_in_flight_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A drop fails the in-flight call at once and hands the socket error to the close hook."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(api_timeout=30, reconnect_delay=60)
    connection = transport.connection
    closed: list[Exception] = []

    @plugin.on_connection_closed
    async def on_closed(error: Exception) -> None:
        closed.append(error)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        call = asyncio.create_task(
            plugin.call_api(
                MoveModelRequest(time_in_seconds=1, values_are_relative_to_model=True),
            ),
        )
        await spin_until(lambda: len(connection.sent) >= 3, "move model request")

        connection.drop()

        async with asyncio.timeout(1):
            with pytest.raises(NetworkError):
                await call

        await spin_until(lambda: bool(closed), "on_connection_closed")
        assert isinstance(closed[0], ConnectionClosedError)
        assert connection.close_code == 1006
        assert plugin.state is PluginState.DISCONNECTED
    finally:
        await finish(plugin, run_task)


async def test_stop_cancels_in_flight_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """`stop()` cancels a pending request instead of failing it."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        call = asyncio.create_task(
            plugin.call_api(
                MoveModelRequest(time_in_seconds=1, values_are_relative_to_model=True),
            ),
        )
        await spin_until(lambda: len(connection.sent) >= 3, "move model request")

        await asyncio.wait_for(plugin.stop(), 1)

        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(call, 1)
    finally:
        await finish(plugin, run_task)


async def test_unanswered_request_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unanswered request expires with `RequestTimeout` and leaves nothing pending."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(api_timeout=0.05)
    connection = transport.connection

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        with pytest.raises(RequestTimeout):
            await asyncio.wait_for(
                plugin.call_api(
                    MoveModelRequest(
                        time_in_seconds=1, values_are_relative_to_model=True
                    ),
                ),
                1,
            )

        assert plugin.req_manager.pending == {}
    finally:
        await finish(plugin, run_task)


async def test_zero_api_timeout_waits_forever(monkeypatch: pytest.MonkeyPatch) -> None:
    """`api_timeout=0` means no deadline: the call stays pending until its answer arrives."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(api_timeout=0)
    connection = transport.connection

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        call = asyncio.create_task(
            plugin.call_api(
                MoveModelRequest(time_in_seconds=1, values_are_relative_to_model=True),
            ),
        )
        await spin_until(lambda: len(connection.sent) >= 3, "move model request")

        assert not call.done()

        request = sent_frame(connection, 2)
        connection.feed(envelope("MoveModelResponse", {}, request["requestID"]))
        response = await asyncio.wait_for(call, 1)
        assert isinstance(response, MoveModelResponse)
    finally:
        await finish(plugin, run_task)


async def test_call_api_without_connection_raises() -> None:
    """A call made before any connection fails with `NetworkError` and registers nothing."""
    plugin = make_plugin()

    with pytest.raises(NetworkError):
        await asyncio.wait_for(
            plugin.call_api(
                MoveModelRequest(time_in_seconds=1, values_are_relative_to_model=True),
            ),
            1,
        )

    assert plugin.req_manager.pending == {}


async def test_call_api_with_explicit_message_type_and_response_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raw data can be sent with an explicit message type and response model."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    payload = {"timeInSeconds": 1, "valuesAreRelativeToModel": True}

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)

        call = asyncio.create_task(
            plugin.call_api(
                payload,
                message_type="MoveModelRequest",
                response_model=MoveModelResponse,
            ),
        )
        await spin_until(lambda: len(connection.sent) >= 3, "raw move model request")

        request = sent_frame(connection, 2)
        assert request["messageType"] == "MoveModelRequest"
        assert request["data"] == payload

        connection.feed(envelope("MoveModelResponse", {}, request["requestID"]))
        response = await asyncio.wait_for(call, 1)
        assert isinstance(response, MoveModelResponse)
    finally:
        await finish(plugin, run_task)


async def test_call_api_requires_message_type_and_response_model_for_raw_data() -> None:
    """Non-model data cannot be sent without a message type and a response model."""
    plugin = make_plugin()
    raw_call = cast("Callable[..., Coroutine[object, object, object]]", plugin.call_api)

    with pytest.raises(TypeError):
        await raw_call({"anything": 1})

    with pytest.raises(TypeError):
        await raw_call({"anything": 1}, message_type="MoveModelRequest")


async def test_send_on_a_closed_connection_raises_network_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A send the socket rejects fails the call with `NetworkError` and forgets it."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await connection.close()

        with pytest.raises(NetworkError):
            await asyncio.wait_for(
                plugin.call_api(
                    MoveModelRequest(
                        time_in_seconds=1, values_are_relative_to_model=True
                    ),
                ),
                1,
            )

        assert plugin.req_manager.pending == {}
    finally:
        await finish(plugin, run_task)
