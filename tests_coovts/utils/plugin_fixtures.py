"""Plugin construction and handshake helpers shared by the plugin tests."""

from typing import TYPE_CHECKING

from coovts.plugin import Plugin, PluginState

from .async_helpers import spin_until
from .frames import envelope, real_payload, sent_frame

if TYPE_CHECKING:
    from .plugin_fake import FakeConnection

PLUGIN_NAME = "coovts-test-plugin"
PLUGIN_DEVELOPER = "coovts"
TOKEN = "test-authentication-token"  # noqa: S105


def make_plugin(
    *,
    api_timeout: float | None = 30,
    reconnect_delay: float = 60,
    authentication_token: str | None = None,
) -> Plugin:
    """Build a plugin pointed at a fake endpoint with a reconnect delay too long to wait for."""
    return Plugin(
        PLUGIN_NAME,
        PLUGIN_DEVELOPER,
        authentication_token=authentication_token,
        endpoint="ws://fake-vts:8001",
        api_timeout=api_timeout,
        reconnect_delay=reconnect_delay,
    )


async def authenticate(plugin: Plugin, connection: "FakeConnection") -> None:
    """Answer the authentication request the plugin sends last, then wait for `AUTHENTICATED`."""
    await spin_until(
        lambda: (
            bool(connection.sent)
            and sent_frame(connection, len(connection.sent) - 1)["messageType"]
            == "AuthenticationRequest"
        ),
        "authentication request",
    )
    request = sent_frame(connection, len(connection.sent) - 1)
    connection.feed(
        envelope(
            "AuthenticationResponse",
            real_payload("AuthenticationResponse"),
            request["requestID"],
        ),
    )
    await spin_until(
        lambda: plugin.state is PluginState.AUTHENTICATED,
        "authenticated state",
    )


async def handshake(plugin: Plugin, connection: "FakeConnection") -> None:
    """Drive the plugin through the token request and the authentication exchange."""
    await spin_until(lambda: len(connection.sent) >= 1, "authentication token request")
    token_request = sent_frame(connection, 0)
    connection.feed(
        envelope(
            "AuthenticationTokenResponse",
            {"authenticationToken": TOKEN},
            token_request["requestID"],
        ),
    )

    await spin_until(lambda: len(connection.sent) >= 2, "authentication request")
    await authenticate(plugin, connection)
