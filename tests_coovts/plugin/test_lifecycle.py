"""Lifecycle of the plugin's connection: failed connects, reconnects and `stop()`."""

import asyncio
import contextlib

import pytest

from coovts.plugin import PluginState
from coovts.types.consts import ErrorID
from coovts.types.event import ModelLoadedEventData

from ..utils.async_helpers import finish, spin_until, tick
from ..utils.frames import envelope, sent_frame
from ..utils.plugin_fake import FakeTransport, FlakyTransport, install_transport
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
