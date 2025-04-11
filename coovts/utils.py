import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Callable
from functools import partial, wraps
from types import CoroutineType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from concurrent.futures import Executor

type C[T] = CoroutineType[Any, Any, T]


def run_sync[**P, R](
    call: Callable[P, R],
    loop: AbstractEventLoop | None = None,
    executor: "Executor | None" = None,
) -> Callable[P, C[R]]:
    @wraps(call)
    async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        _loop = loop or asyncio.get_running_loop()
        return await _loop.run_in_executor(
            executor,
            partial(call, *args, **kwargs),
        )

    return _wrapper
