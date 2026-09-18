"""Lifecycle of the plugin's connection: failed connects, reconnects and `stop()`."""

import asyncio

import pytest

from coovts.plugin import PluginState
from coovts.types.consts import ErrorID
from coovts.types.event import ModelLoadedEventData

from ..utils.async_helpers import finish, spin_until, tick
from ..utils.frames import envelope, sent_frame
from ..utils.plugin_fake import FakeTransport, FlakyTransport, install_transport
from ..utils.plugin_fixtures import TOKEN, handshake, make_plugin


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
        await spin_until(recv_task.cancelled, "the receive task to be cancelled")
    finally:
        await finish(plugin, run_task)
