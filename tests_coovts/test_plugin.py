"""End-to-end tests for `coovts.plugin.Plugin` over a fake WebSocket connection."""

import asyncio
import base64
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest
from websockets.exceptions import ConnectionClosedError

from coovts.errors import (
    APIError,
    AuthenticationFailedError,
    NetworkError,
    RequestTimeout,
)
from coovts.plugin import Plugin, PluginState, dispatch_handlers_inner
from coovts.types.api import (
    APIStateRequest,
    APIStateResponse,
    MoveModelRequest,
    MoveModelResponse,
)
from coovts.types.consts import ErrorID
from coovts.types.event import ModelLoadedEventData, ModelMovedEventData

from .utils.async_helpers import finish, spin_until, tick
from .utils.frames import envelope, real_frame, real_payload, sent_frame
from .utils.plugin_fake import FakeTransport, FlakyTransport, install_transport
from .utils.plugin_fixtures import PLUGIN_NAME, TOKEN, handshake, make_plugin

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine


async def test_handshake_gets_token_then_authenticates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A plugin without a token asks for one, then authenticates with the token it got."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    tokens: list[str] = []
    authenticated: list[bool] = []

    @plugin.on_authentication_token_got
    async def on_token(token: str) -> None:
        tokens.append(token)

    @plugin.on_authenticated
    async def on_authenticated() -> None:
        authenticated.append(True)

    run_task = plugin.run()
    try:
        await spin_until(
            lambda: len(connection.sent) >= 1, "authentication token request"
        )
        token_request = sent_frame(connection, 0)
        assert token_request["messageType"] == "AuthenticationTokenRequest"
        assert token_request["requestID"] is not None
        assert token_request["requestID"].isdigit()
        assert token_request["data"]["pluginName"] == PLUGIN_NAME

        connection.feed(
            envelope(
                "AuthenticationTokenResponse",
                {"authenticationToken": TOKEN},
                token_request["requestID"],
            ),
        )

        await spin_until(lambda: len(connection.sent) >= 2, "authentication request")
        auth_request = sent_frame(connection, 1)
        assert auth_request["messageType"] == "AuthenticationRequest"
        assert auth_request["data"]["authenticationToken"] == TOKEN
        assert auth_request["requestID"] != token_request["requestID"]

        connection.feed(
            envelope(
                "AuthenticationResponse",
                {"authenticated": True, "reason": ""},
                auth_request["requestID"],
            ),
        )

        await spin_until(
            lambda: bool(tokens) and bool(authenticated),
            "authentication hooks",
        )
        assert plugin.state is PluginState.AUTHENTICATED
        assert plugin.authentication_token == TOKEN
        assert tokens == [TOKEN]
        assert authenticated == [True]
    finally:
        await finish(plugin, run_task)


async def test_refused_authentication_reports_to_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A refused authentication reaches `on_authenticate_failed` and drops the stored token."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token="stale-token")  # noqa: S106
    connection = transport.connection
    failures: list[Exception] = []

    @plugin.on_authenticate_failed
    async def on_failed(error: Exception) -> None:
        failures.append(error)

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(connection.sent) >= 1, "authentication request")
        auth_request = sent_frame(connection, 0)
        assert auth_request["messageType"] == "AuthenticationRequest"

        connection.feed(
            envelope(
                "AuthenticationResponse",
                {"authenticated": False, "reason": "token expired"},
                auth_request["requestID"],
            ),
        )

        await spin_until(lambda: bool(failures), "on_authenticate_failed")
        assert len(failures) == 1
        assert isinstance(failures[0], AuthenticationFailedError)
        assert str(failures[0]) == "token expired"

        await spin_until(
            lambda: plugin.state is PluginState.DISCONNECTED,
            "disconnect after a refused authentication",
        )
        assert plugin.authentication_token is None
    finally:
        await finish(plugin, run_task)


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


async def test_event_frame_reaches_matching_handler(
    monkeypatch: pytest.MonkeyPatch,
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
    monkeypatch: pytest.MonkeyPatch,
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


async def test_unparseable_frame_reaches_parse_error_hook(
    monkeypatch: pytest.MonkeyPatch,
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


def test_prepare_icon_encodes_bytes_and_paths(tmp_path: Path) -> None:
    """An icon passes through as text, and bytes or a file path become base64."""
    raw = b"\x89PNG\r\n"
    encoded = base64.b64encode(raw).decode()

    assert (
        Plugin.prepare_icon("data:image/png;base64,abc") == "data:image/png;base64,abc"
    )
    assert Plugin.prepare_icon(raw) == encoded

    icon_file = tmp_path / "icon.png"
    icon_file.write_bytes(raw)
    assert Plugin.prepare_icon(icon_file) == encoded


async def test_drop_reconnects_and_reauthenticates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """After a drop the plugin reconnects and authenticates again with the stored token."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(reconnect_delay=0)
    connection = transport.connection
    sessions: list[bool] = []

    @plugin.on_authenticated
    async def on_authenticated() -> None:
        sessions.append(True)

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        await spin_until(lambda: bool(sessions), "first on_authenticated")

        connection.drop()
        await spin_until(
            lambda: len(connection.sent) >= 3, "authentication after reconnect"
        )

        request = sent_frame(connection, 2)
        assert request["messageType"] == "AuthenticationRequest"
        assert request["data"]["authenticationToken"] == TOKEN

        connection.feed(
            envelope(
                "AuthenticationResponse",
                {"authenticated": True, "reason": ""},
                request["requestID"],
            ),
        )
        await spin_until(lambda: len(sessions) == 2, "second on_authenticated")

        assert plugin.state is PluginState.AUTHENTICATED
        assert transport.endpoints == [plugin.endpoint, plugin.endpoint]
    finally:
        await finish(plugin, run_task)


async def test_unknown_message_type_is_dropped(monkeypatch: pytest.MonkeyPatch) -> None:
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
    monkeypatch: pytest.MonkeyPatch,
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


async def test_failed_connect_reports_transport_error_and_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed connect reaches `on_connect_failed` with the transport's error, then recovers."""
    error = OSError("VTube Studio is not running")
    transport = FlakyTransport(error, failures=1)
    install_transport(monkeypatch, transport)
    plugin = make_plugin(reconnect_delay=0)
    connection = transport.connection
    failures: list[Exception] = []

    @plugin.on_connect_failed
    async def on_failed(failure: Exception) -> None:
        failures.append(failure)

    run_task = plugin.run()
    try:
        await spin_until(lambda: bool(failures), "on_connect_failed")
        assert failures[0] is error

        await handshake(plugin, connection)

        assert transport.attempts == 2
        assert transport.endpoints == [plugin.endpoint, plugin.endpoint]
        assert plugin.state is PluginState.AUTHENTICATED
    finally:
        await finish(plugin, run_task)


async def test_reconnect_while_connecting_is_refused(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A second `reconnect()` while one is in flight is refused instead of racing it."""
    transport = FakeTransport()
    transport.gate = asyncio.Event()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    connecting = asyncio.create_task(plugin.reconnect())
    try:
        await tick()
        assert plugin.state is PluginState.CONNECTING

        with pytest.raises(RuntimeError):
            await plugin.reconnect()
    finally:
        transport.gate.set()
        await asyncio.wait_for(connecting, 1)
        await plugin.stop()


async def test_refused_authentication_retries_with_a_fresh_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """After a refusal the plugin reconnects and asks for a new token, not the rejected one."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(reconnect_delay=0)
    connection = transport.connection
    failures: list[Exception] = []

    @plugin.on_authenticate_failed
    async def on_failed(failure: Exception) -> None:
        failures.append(failure)

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(connection.sent) >= 1, "token request")
        token_request = sent_frame(connection, 0)
        connection.feed(
            envelope(
                "AuthenticationTokenResponse",
                {"authenticationToken": TOKEN},
                token_request["requestID"],
            ),
        )

        await spin_until(lambda: len(connection.sent) >= 2, "authentication request")
        auth_request = sent_frame(connection, 1)
        connection.feed(
            envelope(
                "AuthenticationResponse",
                {"authenticated": False, "reason": "expired"},
                auth_request["requestID"],
            ),
        )

        await spin_until(
            lambda: len(connection.sent) >= 3 and bool(failures),
            "token request after the refusal",
        )

        assert sent_frame(connection, 2)["messageType"] == "AuthenticationTokenRequest"
        assert transport.endpoints == [plugin.endpoint, plugin.endpoint]
    finally:
        await finish(plugin, run_task)


async def test_run_twice_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Starting an already-running plugin raises instead of spawning a second supervisor."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    run_task = plugin.run()
    try:
        with pytest.raises(RuntimeError):
            plugin.run()
    finally:
        await finish(plugin, run_task)


async def test_authenticate_when_already_authenticated_is_a_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An authenticated plugin does not send another authentication request."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        sent = list(connection.sent)

        await asyncio.wait_for(plugin.authenticate(), 1)

        assert connection.sent == sent
        assert plugin.state is PluginState.AUTHENTICATED
    finally:
        await finish(plugin, run_task)


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


async def test_stop_cancels_running_handlers(monkeypatch: pytest.MonkeyPatch) -> None:
    """`stop()` cancels a handler that is still running and waits for it to unwind."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    started = asyncio.Event()
    cancelled: list[bool] = []

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.append(True)
            raise

    run_task = plugin.run()
    try:
        await handshake(plugin, connection)
        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(started.is_set, "handler started")

        await asyncio.wait_for(plugin.stop(), 1)

        assert cancelled == [True]
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


async def test_unknown_payload_fields_are_ignored(
    monkeypatch: pytest.MonkeyPatch,
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


async def test_parked_handler_does_not_block_the_receive_loop(
    monkeypatch: pytest.MonkeyPatch,
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


async def test_authentication_refusal_no_retry_can_fix_stops_the_plugin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A refusal caused by the plugin's own settings stops it instead of looping forever."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection
    failures: list[Exception] = []

    @plugin.on_authenticate_failed
    async def on_failed(error: Exception) -> None:
        failures.append(error)

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(connection.sent) >= 1, "authentication request")
        request = sent_frame(connection, 0)
        connection.feed(
            envelope(
                "APIError",
                {"errorID": ErrorID.TokenRequestDenied, "message": "denied"},
                request["requestID"],
            ),
        )

        await asyncio.wait_for(run_task, 5)

        assert len(failures) == 1
        assert isinstance(failures[0], APIError)
        assert failures[0].data.error_id == ErrorID.TokenRequestDenied
        assert plugin.stopped is True
        assert plugin.state is PluginState.STOPPED
        assert len(transport.endpoints) == 1
    finally:
        await finish(plugin, run_task)


async def test_authentication_refusal_a_retry_can_fix_keeps_looping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A refusal VTS may answer differently next time keeps the supervisor reconnecting."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(connection.sent) >= 1, "authentication request")
        request = sent_frame(connection, 0)
        connection.feed(
            envelope(
                "APIError",
                {
                    "errorID": ErrorID.TokenRequestCurrentlyOngoing,
                    "message": "the request window is open",
                },
                request["requestID"],
            ),
        )

        await spin_until(
            lambda: len(connection.sent) >= 2,
            "second authentication attempt",
        )
        assert plugin.stopped is False

        retry = sent_frame(connection, 1)
        connection.feed(
            envelope(
                "AuthenticationResponse",
                {"authenticated": True, "reason": ""},
                retry["requestID"],
            ),
        )
        await spin_until(
            lambda: plugin.state is PluginState.AUTHENTICATED,
            "authenticated state",
        )
    finally:
        await finish(plugin, run_task)
