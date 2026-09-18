import asyncio
import logging
import sys
from pathlib import Path

from coovts.plugin import Plugin
from coovts.types import api, event, get_event_name

logger = logging.getLogger(__name__)

AUTH_TOKEN_FILE = Path(__file__).parent / "auth_token.txt"
plugin = Plugin(
    "Example Plugin",
    "LgCuwukii",
    Path(__file__).parent / "icon.png",
    authentication_token=(
        AUTH_TOKEN_FILE.read_text().strip() if AUTH_TOKEN_FILE.exists() else None
    ),
)

# region loggings and auth token handle


@plugin.on_connecting
async def _():
    logger.info("Connecting to VTS WS at %s", plugin.endpoint)


@plugin.on_connected
async def _():
    logger.info("Connected to VTS WS, authenticating")


@plugin.on_connect_failed
async def _(e: Exception):
    logger.error(
        "Failed to connect, will retry after %s seconds: %s: %s",
        plugin.reconnect_delay,
        type(e).__name__,
        e,
    )


@plugin.on_connection_closed
async def _(e: Exception):
    if plugin.stopped:
        return
    logger.error(
        "Connection closed, will retry after %s seconds",
        plugin.reconnect_delay,
        exc_info=e,
    )


@plugin.on_disconnect_failed
async def _(e: Exception):
    logger.error("Failed to disconnect cleanly", exc_info=e)


@plugin.on_parse_data_error
async def _(_raw: str | bytes, e: Exception):
    logger.error("Failed to parse data from VTS", exc_info=e)


@plugin.on_authentication_token_got
async def _(token: str):
    logger.info("Authentication token got")
    AUTH_TOKEN_FILE.write_text(token)


@plugin.on_authenticated
async def _():
    logger.info("Authenticated successfully!")


@plugin.on_authenticate_failed
async def _(e: Exception):
    logger.error("Authentication failed: %s: %s", type(e).__name__, e)
    AUTH_TOKEN_FILE.unlink(missing_ok=True)
    logger.warning("Cleared authentication token, please re-authenticate at next retry")


@plugin.on_handler_run_failed
async def _(e: Exception):
    logger.error("Failed to run handler", exc_info=e)


# endregion


# region api calling (event registering) & handling


@plugin.on_authenticated
async def _():
    await plugin.call_api(
        api.EventSubscriptionRequest(
            event_name=get_event_name(event.ModelMovedEventData),
            subscribe=True,
            config=event.ModelMovedEventConfig(),
        ),
    )
    logger.info("Subscribed to ModelMovedEvent")


@plugin.handle_event(event.ModelMovedEventData)
async def _(data: event.ModelMovedEventData):
    logger.info("Model moved: %s", data)


# endregion


async def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    await plugin.run()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
