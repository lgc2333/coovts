# Getting started

> [简体中文](../zh-cn/01-getting-started.md)

## Requirements

Python >= 3.12, and `pip install coovts`.

The library brings no logging of its own: no logging dependency, no log lines. Everything worth
knowing arrives as a hook or an exception
([ADR-0011](../../adr/0011-dependency-set.md)).

## A minimal plugin

```python
import asyncio
import sys
from pathlib import Path

from coovts.plugin import Plugin
from coovts.types import api, event, get_event_name

AUTH_TOKEN_FILE = Path(__file__).parent / "auth_token.txt"

plugin = Plugin(
    "My Plugin",
    "My Name",
    Path(__file__).parent / "icon.png",
    authentication_token=(
        AUTH_TOKEN_FILE.read_text().strip() if AUTH_TOKEN_FILE.exists() else None
    ),
)


@plugin.on_authentication_token_got
async def _(token: str):
    AUTH_TOKEN_FILE.write_text(token)


@plugin.on_authenticate_failed
async def _(e: Exception):
    AUTH_TOKEN_FILE.unlink(missing_ok=True)


@plugin.on_authenticated
async def _():
    await plugin.call_api(
        api.EventSubscriptionRequest(
            event_name=get_event_name(event.ModelMovedEventData),
            subscribe=True,
            config=event.ModelMovedEventConfig(),
        ),
    )


@plugin.handle_event(event.ModelMovedEventData)
async def _(data: event.ModelMovedEventData):
    print("model moved:", data.model_position)


async def main() -> int:
    await plugin.run()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

[`examples/basic.py`](../../../examples/basic.py) is the same thing with every logging hook filled in.

## Three things that bite

### 1. Per-session setup belongs in `on_authenticated`

`on_authenticated` fires **once per session**, including after every reconnect. Event subscriptions
and custom parameters are session-scoped: when the connection drops, VTS forgets them. So anything
that has to exist per session — subscriptions, created parameters, ids you noted down — goes in
`on_authenticated`, not in `main()`. The reasoning is in
[ADR-0007](../../adr/0007-reconnect-is-a-fixed-delay-loop.md).

### 2. The token is yours to keep

- Construct the `Plugin` without `authentication_token` and it first sends an
  `AuthenticationTokenRequest` (with your `plugin_name`, `plugin_developer` and `plugin_icon`), then
  hands you the token through `on_authentication_token_got`. **Persisting it is your job.**
- Pass a token and the library authenticates with it directly, without asking for another.
- When VTS refuses the authentication, the library raises `AuthenticationFailedError` **and clears
  `plugin.authentication_token`**, so the next retry does not slam the same dead token again. That is
  why deleting your stored token in `on_authenticate_failed` is the recommended pattern.
- `plugin_icon` accepts `str` (already base64), `bytes` or a `Path`; the library encodes the latter
  two.
- The flow itself — the popup, what the token means — is upstream documentation:
  [Authentication][s-auth]. So are the hard requirements such as name length.

### 3. VTube Studio being closed does not crash you

`await plugin.run()` does not raise when it cannot connect: a failed connect goes to
`on_connect_failed`, and the supervisor waits `reconnect_delay` (5 seconds by default) before trying
again — forever. Starting the plugin before VTS, or closing VTS and reopening it, are both expected.

To quit, `await plugin.stop()`; do not just cancel the task `run()` handed you.

## Blocking code inside an async program

`run_sync` wraps a blocking callable into a coroutine function that runs it in an executor:

```python
from coovts.utils import run_sync

load_token = run_sync(AUTH_TOKEN_FILE.read_text)
token = await load_token()
```

## Next

- [Connection and lifecycle](./02-lifecycle.md) for the full hook list and its timing.
- [Requests](./03-requests.md) for timeouts, exceptions and field naming.

[s-auth]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#authentication
