import asyncio
import sys
from pathlib import Path

from coovts.plugin import Plugin
from loguru import logger

AUTH_TOKEN_FILE = Path(__file__).parent / "auth_token.txt"
plugin = Plugin(
    "Example Plugin",
    "LgCookie",
    authentication_token=(
        AUTH_TOKEN_FILE.read_text().strip() if AUTH_TOKEN_FILE.exists() else None
    ),
)

# region loggings and auth token handle


@plugin.on_connecting
async def _():
    logger.info(f"Connecting to VTS WS at {plugin.endpoint}")


@plugin.on_connected
async def _():
    logger.info("Connected to VTS WS, authenticating")


@plugin.on_connect_failed
async def _(e: Exception):
    logger.error(
        f"Failed to connect, will retry after {plugin.reconnect_delay} seconds"
        f": {type(e).__name__}: {e}",
    )


@plugin.on_connection_closed
async def _(e: Exception):
    if plugin.stopped:
        return
    logger.opt(exception=e).error(
        f"Connection closed, will retry after {plugin.reconnect_delay} seconds",
    )


@plugin.on_parse_data_error
async def _(_raw: str | bytes, e: Exception):
    logger.opt(exception=e).error("Failed to parse data from VTS")


@plugin.on_authentication_token_got
async def _(token: str):
    logger.success("Authentication token got")
    AUTH_TOKEN_FILE.write_text(token)


@plugin.on_authenticated
async def _():
    logger.success("Authenticated successfully!")


@plugin.on_authenticate_failed
async def _(e: Exception):
    logger.error(f"Authentication failed: {type(e).__name__}: {e}")
    AUTH_TOKEN_FILE.unlink(missing_ok=True)
    logger.warning("Cleared authentication token, please re-authenticate at next retry")


@plugin.on_handler_run_failed
async def _(e: Exception):
    logger.opt(exception=e).error("Failed to run handler")


# endregion


async def main() -> int:
    await plugin.run()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
