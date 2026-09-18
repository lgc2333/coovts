import asyncio
import logging
import sys
from pathlib import Path

from coovts.plugin import Plugin, PluginState
from coovts.types import api, event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
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
    if plugin.state is PluginState.STOPPED:
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

    model = await plugin.call_api(api.CurrentModelRequest())
    logger.info("Current model: %s (%s)", model.model_name, model.model_id)


@plugin.on_authenticate_failed
async def _(e: Exception):
    logger.error("Authentication failed: %s: %s", type(e).__name__, e)
    AUTH_TOKEN_FILE.unlink(missing_ok=True)
    logger.warning("Cleared authentication token, please re-authenticate at next retry")


@plugin.on_handler_run_failed
async def _(e: Exception):
    logger.error("Failed to run handler", exc_info=e)


# endregion


# region event declaring & handling


# declared once, re-subscribed after every authentication; a refusal reaches on_subscribe_failed
# you can dispose it by `await _model_moved_handler.dispose()`
@plugin.subscribe_event(event.ModelMovedEventData)
async def _model_moved_handler(data: event.ModelMovedEventData):
    logger.info("Model moved: %s", data)


# endregion


async def main() -> int:
    await plugin.run()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
