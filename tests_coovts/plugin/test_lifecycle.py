"""Lifecycle of the plugin's connection: failed connects, reconnects and `stop()`."""

import asyncio
import contextlib
import gc
from typing import Any

import pytest
from websockets.exceptions import ConnectionClosedError

from coovts.errors import APIError, NetworkError
from coovts.event import EventRegistration
from coovts.plugin import PluginState
from coovts.types.api import APIStateRequest
from coovts.types.consts import ErrorID
from coovts.types.event import ModelLoadedEventData, ModelOutlineEventData

from ..utils.async_helpers import finish, spin_until, tick
from ..utils.frames import (
    envelope,
    real_error_payload,
    real_payload,
    sent_frame,
)
from ..utils.plugin_fake import (
    DyingTransport,
    FakeTransport,
    FlakyTransport,
    install_transport,
)
from ..utils.plugin_fixtures import TOKEN, authenticate, handshake, make_plugin


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


async def test_a_reconnect_while_one_is_in_flight_opens_no_second_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A second `reconnect()` during a connect does nothing: the connect in flight is its ask."""
    transport = FakeTransport()
    transport.gate = asyncio.Event()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    connecting = asyncio.create_task(plugin.reconnect())
    try:
        await tick()
        assert plugin.state is PluginState.CONNECTING

        await asyncio.wait_for(plugin.reconnect(), 1)

        assert transport.endpoints == [plugin.endpoint]
        assert plugin.state is PluginState.CONNECTING

        waiting = asyncio.create_task(plugin.reconnect(wait_connect=True))
        await tick()
        assert waiting.done() is False

        transport.gate.set()
        await asyncio.wait_for(waiting, 1)
        assert plugin.state is PluginState.AUTHENTICATING
    finally:
        transport.gate.set()
        await asyncio.wait_for(connecting, 1)
        await plugin.stop()


async def test_stopping_during_a_connect_leaves_the_plugin_stopped(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A `stop()` while the socket is being opened ends as `STOPPED`, not as disconnected."""
    transport = FakeTransport()
    transport.gate = asyncio.Event()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(transport.endpoints) == 1, "connect attempt")

        await plugin.stop()

        assert plugin.state is PluginState.STOPPED

        transport.gate.set()
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.wait_for(run_task, 1)

        assert plugin.state is PluginState.STOPPED
    finally:
        transport.gate.set()
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


async def test_failed_disconnect_reaches_its_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A teardown the plugin runs on its own reports a refusing close to `on_disconnect_failed`."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection
    failures: list[Exception] = []
    close_error = OSError("the socket refused to close")

    @plugin.on_disconnect_failed
    async def on_failed(failure: Exception) -> None:
        failures.append(failure)

    async def refusing_close() -> None:
        raise close_error

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(connection.sent) >= 1, "authentication request")
        # the teardown must cancel the running receive task even though the close refused
        recv_task = plugin._recv_task  # noqa: SLF001
        monkeypatch.setattr(connection, "close", refusing_close)

        request = sent_frame(connection, 0)
        connection.feed(
            envelope(
                "APIError",
                {"errorID": ErrorID.TokenRequestDenied, "message": "denied"},
                request["requestID"],
            ),
        )

        await asyncio.wait_for(run_task, 5)

        assert failures == [close_error]
        assert plugin.state is PluginState.STOPPED
        assert recv_task is not None
        await spin_until(recv_task.done, "the receive loop to end")
    finally:
        await finish(plugin, run_task)


async def test_reconnect_leaves_the_run_supervising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A manual `reconnect()` opens a fresh session and the run keeps healing after it."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)
        attempts = len(transport.endpoints)

        await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)

        assert len(transport.endpoints) == attempts + 1
        assert plugin.state is PluginState.AUTHENTICATING
        await authenticate(plugin, connection)
        assert run_task.done() is False

        connection.drop()
        await spin_until(
            lambda: len(transport.endpoints) == attempts + 2,
            "a reconnect after the drop",
        )
        await authenticate(plugin, connection)

        assert run_task.done() is False
        assert plugin.state is PluginState.AUTHENTICATED
    finally:
        await finish(plugin, run_task)


async def test_reconnect_cuts_a_waiting_drop_short(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`reconnect()` makes a run that is waiting out `reconnect_delay` connect now."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=60)
    connection = transport.connection

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)
        attempts = len(transport.endpoints)

        connection.drop()
        await spin_until(
            lambda: plugin.state is PluginState.DISCONNECTED,
            "the drop to be noticed",
        )

        await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)

        assert len(transport.endpoints) == attempts + 1
        assert plugin.state is PluginState.AUTHENTICATING
        assert run_task.done() is False
    finally:
        await finish(plugin, run_task)


async def test_two_reconnects_at_once_open_one_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two `reconnect()` calls in the same tick ask for one fresh session, not two."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=60)
    connection = transport.connection

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)
        attempts = len(transport.endpoints)

        await asyncio.wait_for(
            asyncio.gather(plugin.reconnect(), plugin.reconnect()),
            1,
        )
        await spin_until(
            lambda: len(transport.endpoints) > attempts,
            "the fresh connect",
        )
        await tick(20)

        assert len(transport.endpoints) == attempts + 1
        assert run_task.done() is False
    finally:
        await finish(plugin, run_task)


async def test_a_deliberate_disconnect_reports_no_connection_loss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reconnecting by hand and stopping both end the session without reporting a loss."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection
    closed: list[Exception] = []

    @plugin.on_connection_closed
    async def on_closed(failure: Exception) -> None:
        closed.append(failure)

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)

        await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)
        await authenticate(plugin, connection)

        await asyncio.wait_for(plugin.stop(), 1)

        assert closed == []
        assert plugin.state is PluginState.STOPPED
    finally:
        await finish(plugin, run_task)


async def test_a_drop_while_authenticating_is_not_a_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `reconnect()` during the handshake is not reported as a refused authentication."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection
    failures: list[Exception] = []

    @plugin.on_authenticate_failed
    async def on_failed(failure: Exception) -> None:
        failures.append(failure)

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(connection.sent) >= 1, "authentication request")

        await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)
        await authenticate(plugin, connection)

        assert failures == []
        assert plugin.state is PluginState.AUTHENTICATED
    finally:
        await finish(plugin, run_task)


async def test_wait_connect_gives_up_when_the_run_ends(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `wait_connect` wait ends with the run instead of outliving it."""
    transport = FakeTransport()
    transport.gate = asyncio.Event()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(transport.endpoints) == 1, "connect attempt")

        waiting = asyncio.create_task(plugin.reconnect(wait_connect=True))
        await tick()
        assert waiting.done() is False

        await asyncio.wait_for(plugin.stop(), 1)

        await asyncio.wait_for(waiting, 1)
        assert plugin.state is PluginState.STOPPED
    finally:
        transport.gate.set()
        await finish(plugin, run_task)


async def test_a_peer_that_vanishes_during_a_drop_is_not_a_connection_loss(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A peer that dies as the session is dropped ends the loop quietly, not as a loss."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=60)
    connection = transport.connection
    closed: list[Exception] = []

    @plugin.on_connection_closed
    async def on_closed(failure: Exception) -> None:
        closed.append(failure)

    closing = connection.close

    async def close_after_the_peer_vanished() -> None:
        connection.drop()
        await tick()
        await closing()

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)
        attempts = len(transport.endpoints)
        monkeypatch.setattr(connection, "close", close_after_the_peer_vanished)

        await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)

        assert len(transport.endpoints) == attempts + 1
        assert closed == []
    finally:
        await finish(plugin, run_task)


async def test_every_connect_reports_connecting_and_connected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`on_connecting` fires before each attempt and `on_connected` once the socket is up."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection
    connecting: list[bool] = []
    connected: list[bool] = []

    @plugin.on_connecting
    async def on_connecting() -> None:
        connecting.append(True)

    @plugin.on_connected
    async def on_connected() -> None:
        connected.append(True)

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)

        connection.drop()
        await spin_until(
            lambda: len(transport.endpoints) == 2,
            "the reconnect after the drop",
        )
        await authenticate(plugin, connection)

        assert connecting == [True, True]
        assert connected == [True, True]
    finally:
        await finish(plugin, run_task)


async def test_stop_cancels_handlers_even_when_the_close_refuses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A `stop()` whose close fails still cancels the handler that is running."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()
    connection = transport.connection
    started = asyncio.Event()
    cancelled: list[bool] = []
    close_error = OSError("the socket refused to close")

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.append(True)
            raise

    async def refusing_close() -> None:
        raise close_error

    closing = connection.close
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
        monkeypatch.setattr(connection, "close", refusing_close)

        with pytest.raises(OSError, match="refused to close"):
            await asyncio.wait_for(plugin.stop(), 1)

        assert cancelled == [True]
        assert plugin.state is PluginState.STOPPED
    finally:
        monkeypatch.setattr(connection, "close", closing)
        await finish(plugin, run_task)


async def test_reconnect_survives_a_refused_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A close that fails reaches `on_disconnect_failed`, and the run opens the next session."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection
    failures: list[Exception] = []
    close_error = OSError("the socket refused to close")

    @plugin.on_disconnect_failed
    async def on_failed(error: Exception) -> None:
        failures.append(error)

    async def refusing_close() -> None:
        raise close_error

    closing = connection.close
    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)
        attempts = len(transport.endpoints)
        monkeypatch.setattr(connection, "close", refusing_close)

        await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)
        await authenticate(plugin, connection)

        assert failures == [close_error]
        assert len(transport.endpoints) == attempts + 1
        assert plugin.state is PluginState.AUTHENTICATED
    finally:
        monkeypatch.setattr(connection, "close", closing)
        await finish(plugin, run_task)


async def test_a_waiter_shares_the_failure_of_the_connect_it_waited_for(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed connect reaches every caller that waited on it, not only the one that started it."""
    error = OSError("VTube Studio is not running")
    transport = FlakyTransport(error, failures=1)
    transport.gate = asyncio.Event()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    connecting = asyncio.create_task(plugin.reconnect())
    try:
        await spin_until(lambda: len(transport.endpoints) == 1, "connect attempt")
        waiting = asyncio.create_task(plugin.reconnect(wait_connect=True))
        await tick()
        assert waiting.done() is False

        transport.gate.set()

        with pytest.raises(OSError, match="not running"):
            await asyncio.wait_for(connecting, 1)
        with pytest.raises(OSError, match="not running"):
            await asyncio.wait_for(waiting, 1)
    finally:
        transport.gate.set()
        await plugin.stop()


async def test_stop_ends_a_connect_nobody_supervises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`stop()` cancels the connect a manual `reconnect()` owns, so no socket outlives it."""
    transport = FakeTransport()
    transport.gate = asyncio.Event()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    connecting = asyncio.create_task(plugin.reconnect())
    try:
        await spin_until(
            lambda: plugin.state is PluginState.CONNECTING,
            "connect attempt",
        )

        await asyncio.wait_for(plugin.stop(), 1)
        transport.gate.set()

        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(connecting, 1)
        await tick()
        assert plugin.client is None
        assert plugin.state is PluginState.STOPPED
    finally:
        transport.gate.set()
        await plugin.stop()


async def test_a_stopped_plugin_refuses_a_hand_connect_until_it_runs_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`stop()` is final for `reconnect()`; `run()` is what starts the plugin again."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)

    await plugin.stop()
    with pytest.raises(RuntimeError, match="stopped"):
        await plugin.reconnect()

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(transport.endpoints) == 1, "connect attempt")

        await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)

        assert plugin.state is PluginState.AUTHENTICATING
    finally:
        await finish(plugin, run_task)


async def test_a_drop_while_resubscribing_does_not_reach_on_authenticated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A session that dies while its events are re-sent never hands a live session to the hook."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=0)
    connection = transport.connection
    authenticated: list[bool] = []
    refusals: list[Exception] = []

    @plugin.on_authenticated
    async def on_authenticated() -> None:
        authenticated.append(True)

    @plugin.on_subscribe_failed
    async def on_subscribe_failed(
        registration: EventRegistration[Any],
        error: Exception,
    ) -> None:
        refusals.append(error)

    plugin.subscribe_event(ModelOutlineEventData)

    run_task = plugin.run()
    try:
        await authenticate(
            plugin, connection
        )  # authenticated, re-subscription still in flight

        connection.drop()
        await spin_until(lambda: len(transport.endpoints) == 2, "the next session")

        assert authenticated == []
        assert len(refusals) == 1
        assert isinstance(refusals[0], NetworkError)
    finally:
        await finish(plugin, run_task)


async def test_a_run_started_while_stopping_is_not_forgotten(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`stop()` forgets only the run it ended, so a run started mid-stop can still be stopped."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN)
    connection = transport.connection
    gate = asyncio.Event()
    started: list[bool] = []
    unwinding: list[bool] = []

    @plugin.handle_event(ModelLoadedEventData)
    async def on_loaded(data: ModelLoadedEventData) -> None:
        started.append(True)
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            unwinding.append(True)
            await gate.wait()  # the stop waits here, with its run already ended
            raise

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)
        connection.feed(
            envelope(
                "ModelLoadedEvent",
                {"modelLoaded": True, "modelName": "model-a", "modelID": "id-1"},
            ),
        )
        await spin_until(lambda: bool(started), "the handler to start")

        stopping = asyncio.create_task(plugin.stop())
        await spin_until(lambda: bool(unwinding), "the stop to reach its sweep")
        sent_before = len(connection.sent)
        second_run = plugin.run()
        await spin_until(
            lambda: len(connection.sent) == sent_before + 1,
            "the second session's authentication request",
        )
        await authenticate(plugin, connection)  # started mid-stop, it gets a session

        gate.set()
        await asyncio.wait_for(stopping, 1)

        await asyncio.wait_for(plugin.stop(), 1)
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.wait_for(second_run, 1)

        attempts = len(transport.endpoints)
        await tick(50)  # a run that was forgotten connects again here

        assert second_run.done()
        assert len(transport.endpoints) == attempts
        assert plugin.state is PluginState.STOPPED
    finally:
        gate.set()
        await finish(plugin, run_task)


async def test_a_request_failed_mid_send_leaves_nothing_for_the_loop_to_log(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A disconnect that fails a request mid-send leaves no exception for the loop to report."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN)
    connection = transport.connection
    logged: list[str] = []
    loop = asyncio.get_running_loop()
    previous = loop.get_exception_handler()
    loop.set_exception_handler(
        lambda _loop, context: logged.append(str(context["message"])),
    )

    async def send_after_the_drop(payload: str) -> None:
        connection.drop()
        await tick(
            20
        )  # the receive loop fails the pending request before the send gives up
        raise ConnectionClosedError(None, None)

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)
        monkeypatch.setattr(connection, "send", send_after_the_drop)

        with pytest.raises(NetworkError, match="lost"):
            await plugin.call_api(APIStateRequest())

        gc.collect()
        await tick()
        assert logged == []
    finally:
        loop.set_exception_handler(previous)
        await finish(plugin, run_task)


async def test_two_stops_at_once_leave_the_plugin_stopped(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two `stop()` calls in the same tick both return, with no session left behind."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN)
    connection = transport.connection

    run_task = plugin.run()
    try:
        await authenticate(plugin, connection)

        await asyncio.wait_for(asyncio.gather(plugin.stop(), plugin.stop()), 2)

        assert plugin.state is PluginState.STOPPED
        assert plugin.client is None
        assert run_task.done()
    finally:
        with contextlib.suppress(asyncio.CancelledError):
            await run_task


async def test_a_fatal_refusal_that_arrives_with_a_close_still_ends_the_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A refusal no retry can fix stops the plugin even when the socket dies with it."""
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
        await spin_until(lambda: bool(connection.sent), "authentication request")
        request = sent_frame(connection, len(connection.sent) - 1)
        connection.feed(
            envelope(
                "APIError",
                real_error_payload(ErrorID.TokenRequestDenied),
                request["requestID"],
            ),
        )
        connection.drop()  # the socket dies in the same receive step as the refusal
        await tick(80)

        assert len(failures) == 1
        assert isinstance(failures[0], APIError)
        assert plugin.state is PluginState.STOPPED
        assert len(transport.endpoints) == 1  # no retry loop
    finally:
        await finish(plugin, run_task)


async def test_a_socket_that_died_during_resubscribing_does_not_reach_on_authenticated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A socket that is already closed when re-subscription ends never reaches the hook.

    The receive loop may not have noticed the close yet, so the socket's own state is what decides.
    """
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=60)
    connection = transport.connection
    authenticated: list[bool] = []
    refusals: list[Exception] = []
    gate = asyncio.Event()
    parked: list[bool] = []
    sending = connection.send

    async def park_the_resubscribe(payload: str) -> None:
        if not parked and "EventSubscriptionRequest" in payload:
            parked.append(True)
            await gate.wait()
        await sending(payload)

    @plugin.on_authenticated
    async def on_authenticated() -> None:
        authenticated.append(True)

    @plugin.on_subscribe_failed
    async def on_subscribe_failed(
        registration: EventRegistration[Any],
        error: Exception,
    ) -> None:
        refusals.append(error)

    plugin.subscribe_event(ModelOutlineEventData)

    run_task = plugin.run()
    try:
        await spin_until(lambda: bool(connection.sent), "authentication request")
        request = sent_frame(connection, len(connection.sent) - 1)
        monkeypatch.setattr(connection, "send", park_the_resubscribe)
        connection.feed(
            envelope(
                "AuthenticationResponse",
                real_payload("AuthenticationResponse"),
                request["requestID"],
            ),
        )
        await spin_until(lambda: bool(parked), "the re-subscription to park")

        connection.closed = (
            True  # the peer is gone; the receive loop has not noticed yet
        )
        connection.close_code = 1006
        gate.set()
        await tick(80)

        assert len(refusals) == 1
        assert isinstance(refusals[0], NetworkError)
        assert authenticated == []
    finally:
        gate.set()
        monkeypatch.setattr(connection, "send", sending)
        await finish(plugin, run_task)


async def test_a_socket_that_dies_during_the_handshake_waits_out_the_delay(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A drop under the handshake retries on the fixed delay, not at loop speed (ADR-0007)."""
    transport = DyingTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=60)

    run_task = plugin.run()
    try:
        await spin_until(lambda: len(transport.endpoints) == 1, "the first connect")

        await tick(400)

        assert len(transport.endpoints) == 1
    finally:
        await finish(plugin, run_task)


async def test_a_cancelled_caller_leaves_the_connect_for_the_others(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A caller that gives up does not cancel the plugin's connect under the callers still waiting."""
    transport = FakeTransport()
    transport.gate = asyncio.Event()
    install_transport(monkeypatch, transport)
    plugin = make_plugin()

    first = asyncio.create_task(plugin.reconnect())
    try:
        await spin_until(lambda: len(transport.endpoints) == 1, "connect attempt")
        second = asyncio.create_task(plugin.reconnect(wait_connect=True))
        await tick()
        assert second.done() is False

        first.cancel()
        await tick()
        transport.gate.set()
        await asyncio.wait_for(second, 1)

        assert first.cancelled() is True
        assert second.cancelled() is False
        assert plugin.state is PluginState.AUTHENTICATING
    finally:
        transport.gate.set()
        await plugin.stop()


async def test_a_teardown_close_that_fails_is_not_a_connect_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The leading disconnect of a session reports a refusing close to its own hook."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(authentication_token=TOKEN, reconnect_delay=60)
    connection = transport.connection
    disconnect_failures: list[Exception] = []
    connect_failures: list[Exception] = []
    close_error = OSError("the socket refused to close")

    async def refusing_close() -> None:
        raise close_error

    close = connection.close

    @plugin.on_disconnect_failed
    async def on_disconnect_failed(error: Exception) -> None:
        disconnect_failures.append(error)

    @plugin.on_connect_failed
    async def on_connect_failed(error: Exception) -> None:
        connect_failures.append(error)

    await asyncio.wait_for(plugin.reconnect(wait_connect=True), 1)
    monkeypatch.setattr(connection, "close", refusing_close)

    run_task = plugin.run()
    try:
        await spin_until(lambda: bool(disconnect_failures), "on_disconnect_failed")

        assert disconnect_failures == [close_error]
        assert connect_failures == []
    finally:
        monkeypatch.setattr(connection, "close", close)
        await finish(plugin, run_task)
