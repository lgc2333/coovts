"""A fake `websockets` client connection and the patch that installs it on `coovts.plugin`."""

import asyncio
from typing import TYPE_CHECKING

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

if TYPE_CHECKING:
    import pytest


class FakeConnection:
    """A fake client connection: recorded outbound frames, queued inbound ones."""

    def __init__(self) -> None:
        self.sent: list[str] = []
        """Every payload handed to `send`, in order."""
        self.close_code: int | None = None
        self.closed = False
        self._inbound: asyncio.Queue[str | BaseException] = asyncio.Queue()
        self._reading = False

    def feed(self, frame: str) -> None:
        """Queue one raw frame for the next `recv` call."""
        self._inbound.put_nowait(frame)

    def drop(self) -> None:
        """Make the next `recv` raise, the way a lost connection does."""
        self.closed = True
        self.close_code = 1006
        self._inbound.put_nowait(ConnectionClosedError(None, None))

    async def send(self, payload: str) -> None:
        """Record an outbound payload, refusing to send once closed."""
        if self.closed:
            raise ConnectionClosedError(None, None)
        self.sent.append(payload)

    async def recv(self) -> str:
        """Return the next queued frame, or raise the queued failure."""
        self._reading = True
        try:
            item = await self._inbound.get()
        finally:
            self._reading = False
        if isinstance(item, BaseException):
            raise item
        return item

    async def close(self) -> None:
        """Close the connection the way `websockets` would, failing a read left waiting."""
        self.closed = True
        self.close_code = 1000
        if self._reading:
            self._inbound.put_nowait(ConnectionClosedOK(None, None))

    def reopen(self) -> None:
        """Make the connection usable again, as a new session on a fresh socket would."""
        self.closed = False
        self.close_code = None
        while not self._inbound.empty():
            self._inbound.get_nowait()


class FakeTransport:
    """Stand-in for `websockets.connect`, handing out one `FakeConnection`.

    `self.connection` is the object a test drives before the plugin connects; a reconnect
    reuses it (`reopen`), so `sent` keeps the whole session history in order.
    """

    def __init__(self) -> None:
        self.connection = FakeConnection()
        self.endpoints: list[str] = []
        self.gate: asyncio.Event | None = None
        """When set, `connect` waits for it before handing the connection out."""

    async def connect(self, endpoint: str) -> FakeConnection:
        """Record the endpoint and return the shared connection."""
        self.endpoints.append(endpoint)
        await self.wait_gate()
        self.connection.reopen()
        return self.connection

    async def wait_gate(self) -> None:
        """Park on the gate when one is set, so a test can hold a connect open."""
        if self.gate is not None:
            await self.gate.wait()


class FlakyTransport(FakeTransport):
    """A transport whose first `failures` connects fail, like VTube Studio still starting."""

    def __init__(self, error: Exception, failures: int) -> None:
        super().__init__()
        self.error = error
        self.failures = failures
        self.attempts = 0

    async def connect(self, endpoint: str) -> FakeConnection:
        """Raise the configured failure for the first `failures` attempts, then connect."""
        self.attempts += 1
        if self.attempts <= self.failures:
            self.endpoints.append(endpoint)
            await self.wait_gate()
            raise self.error
        return await super().connect(endpoint)


class DyingTransport(FakeTransport):
    """A transport whose socket completes the handshake and dies on its first read.

    A port forwarder that accepts then resets, or VTube Studio restarting mid-handshake.
    """

    async def connect(self, endpoint: str) -> FakeConnection:
        """Hand out a connection that fails the next read, like a socket that died at once."""
        connection = await super().connect(endpoint)
        connection.drop()
        return connection


def install_transport(
    monkeypatch: "pytest.MonkeyPatch", transport: FakeTransport
) -> None:
    """Point `coovts.plugin`'s connect at `transport` for the duration of a test."""
    monkeypatch.setattr("coovts.plugin.ws.connect", transport.connect)
