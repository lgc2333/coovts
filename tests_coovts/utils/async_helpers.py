"""Helpers that drive the plugin's background tasks deterministically, without real timers."""

import asyncio
import contextlib
from collections.abc import Callable

from coovts.plugin import Plugin


async def tick(times: int = 5) -> None:
    """Let the plugin's tasks run a few steps."""
    for _ in range(times):
        await asyncio.sleep(0)


async def spin_until(condition: Callable[[], bool], expected: str) -> None:
    """Let the plugin's tasks run until `condition` holds, failing if it never does."""
    for _ in range(500):
        if condition():
            return
        await asyncio.sleep(0)
    raise AssertionError(f"never observed: {expected}")


async def finish(plugin: Plugin, run_task: asyncio.Task[None]) -> None:
    """Stop the plugin and settle the supervisor task it returned."""
    await asyncio.wait_for(plugin.stop(), 1)
    with contextlib.suppress(asyncio.CancelledError):
        await asyncio.wait_for(run_task, 1)
