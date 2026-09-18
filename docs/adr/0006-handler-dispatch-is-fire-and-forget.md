# Handler dispatch is fire-and-forget

**Status**: accepted

`dispatch_handlers` turns every registered handler into its own `create_task` and returns the task
list to a caller that ignores it. The tasks are held until they complete, which is all `stop()` needs
to cancel and await them; nothing is awaited per frame and nothing is throttled. A handler's
exception is caught inside the task and re-dispatched to `on_handler_run_failed`; `BaseException`
(cancellation, in particular) escapes that catch.

Handlers are fire-and-forget by design: the library never bubbles a handler's outcome back to whoever
dispatched the frame.

## Consequences

- Handler order is not a guarantee. Two handlers for the same event run concurrently, and a slow
  handler does not hold up the next frame, so handlers must not assume they finished before the
  next one started.
- Failures are invisible at the call site: a `raise` inside a handler produces a hook call, not an
  exception in `run()`. Without an `on_handler_run_failed` handler the exception is dropped.
- `stop()` cancels every in-flight handler and awaits it, so a handler must tolerate cancellation:
  a shutdown inside a handler arrives as `asyncio.CancelledError`, and a handler that swallows or
  blocks on it delays the application's exit.
- There is no backpressure: a handler that lags behind the event rate accumulates tasks instead of
  slowing the stream.
