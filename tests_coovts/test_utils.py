async def test_run_sync_returns_blocking_call_result() -> None:
    """Awaiting the wrapper yields the value the blocking callable returns."""
    from coovts.utils import run_sync

    def double(value: int) -> int:
        return value * 2

    wrapper = run_sync(double)

    assert await wrapper(21) == 42


async def test_run_sync_forwards_arguments_intact() -> None:
    """Positional, keyword and keyword-only arguments all reach the blocking callable."""
    from coovts.utils import run_sync

    def describe(prefix: str, count: int, *, suffix: str, sep: str = "-") -> str:
        return sep.join([prefix, str(count), suffix])

    wrapper = run_sync(describe)

    assert await wrapper("a", 2, suffix="b", sep="+") == "a+2+b"


async def test_run_sync_uses_given_executor() -> None:
    """The executor passed to `run_sync` is the one that runs the blocking callable."""
    from concurrent.futures import ThreadPoolExecutor
    from threading import current_thread

    from coovts.utils import run_sync

    names: list[str] = []

    def record_thread_name() -> None:
        names.append(current_thread().name)

    with ThreadPoolExecutor(thread_name_prefix="probe") as executor:
        wrapper = run_sync(record_thread_name, executor=executor)
        await wrapper()

    assert len(names) == 1
    assert names[0].startswith("probe")


async def test_run_sync_runs_callable_off_event_loop_thread() -> None:
    """The blocking callable runs on another thread than the event loop's."""
    from threading import get_ident

    from coovts.utils import run_sync

    caller_thread = get_ident()
    seen: list[int] = []

    def record_thread() -> None:
        seen.append(get_ident())

    wrapper = run_sync(record_thread)

    await wrapper()

    assert len(seen) == 1
    assert seen[0] != caller_thread
