"""The authentication handshake and the plugin's policy on refused tokens."""

import asyncio

import pytest

from coovts.errors import APIError, AuthenticationFailedError
from coovts.plugin import PluginState
from coovts.types.consts import ErrorID

from ..utils.async_helpers import finish, spin_until
from ..utils.frames import envelope, sent_frame
from ..utils.plugin_fake import FakeTransport, install_transport
from ..utils.plugin_fixtures import PLUGIN_NAME, TOKEN, handshake, make_plugin

FATAL_REFUSALS = [
    ErrorID.APIAccessDeactivated,
    ErrorID.JSONInvalid,
    ErrorID.APINameInvalid,
    ErrorID.APIVersionInvalid,
    ErrorID.TokenRequestDenied,
    ErrorID.TokenRequestPluginNameInvalid,
    ErrorID.TokenRequestDeveloperNameInvalid,
    ErrorID.TokenRequestPluginIconInvalid,
    ErrorID.AuthenticationTokenMissing,
    ErrorID.AuthenticationPluginNameMissing,
    ErrorID.AuthenticationPluginDeveloperMissing,
]
"""Every refusal a retry cannot fix: the plugin stops instead of asking again (ADR-0016)."""

RETRYABLE_REFUSALS = [
    ErrorID.RequestIDInvalid,
    ErrorID.RequestTypeUnknown,
    ErrorID.TokenRequestCurrentlyOngoing,
]
"""Refusals that say nothing about the next attempt, so the plugin tries again."""


async def test_handshake_gets_token_then_authenticates(
    monkeypatch: "pytest.MonkeyPatch",
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
    monkeypatch: "pytest.MonkeyPatch",
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


async def test_drop_reconnects_and_reauthenticates(
    monkeypatch: "pytest.MonkeyPatch",
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


async def test_refused_authentication_retries_with_a_fresh_token(
    monkeypatch: "pytest.MonkeyPatch",
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


async def test_authenticate_when_already_authenticated_is_a_noop(
    monkeypatch: "pytest.MonkeyPatch",
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


@pytest.mark.parametrize("error_id", FATAL_REFUSALS, ids=lambda e: e.name)
async def test_a_refusal_no_retry_can_fix_stops_the_plugin(
    monkeypatch: "pytest.MonkeyPatch",
    error_id: ErrorID,
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
                {"errorID": error_id, "message": "refused"},
                request["requestID"],
            ),
        )

        await asyncio.wait_for(run_task, 5)

        assert len(failures) == 1
        assert isinstance(failures[0], APIError)
        assert failures[0].data.error_id == error_id
        assert plugin.state is PluginState.STOPPED
        assert len(transport.endpoints) == 1
    finally:
        await finish(plugin, run_task)


@pytest.mark.parametrize("error_id", RETRYABLE_REFUSALS, ids=lambda e: e.name)
async def test_a_refusal_a_retry_can_fix_keeps_looping(
    monkeypatch: "pytest.MonkeyPatch",
    error_id: ErrorID,
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
                {"errorID": error_id, "message": "not now"},
                request["requestID"],
            ),
        )

        await spin_until(
            lambda: len(connection.sent) >= 2,
            "second authentication attempt",
        )

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


async def test_the_human_answered_token_request_is_not_cut_short_by_the_api_timeout(
    monkeypatch: "pytest.MonkeyPatch",
) -> None:
    """A popup nobody has clicked yet is waited for, not abandoned and asked again (ADR-0016)."""
    transport = FakeTransport()
    install_transport(monkeypatch, transport)
    plugin = make_plugin(api_timeout=0.01, reconnect_delay=0)
    connection = transport.connection
    failures: list[Exception] = []

    @plugin.on_authenticate_failed
    async def on_failed(failure: Exception) -> None:
        failures.append(failure)

    run_task = plugin.run()
    try:
        await spin_until(
            lambda: len(connection.sent) >= 1, "authentication token request"
        )
        # Real time passes, because the deadline being beaten is a wall-clock one.
        await asyncio.sleep(0.1)

        assert len(transport.endpoints) == 1
        assert len(connection.sent) == 1
        assert failures == []
    finally:
        await finish(plugin, run_task)
