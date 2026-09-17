# Handlers run as untracked tasks

**Status**: accepted

`dispatch_handlers` turns every registered handler into its own `create_task` and returns the task
list to a caller that drops it. A handler's exception is caught inside the task and re-dispatched to
`on_handler_run_failed`; `BaseException` (cancellation, in particular) escapes that catch. Nothing
is awaited, nothing is stored, nothing is throttled.

The receive loop must never be blocked by user code: one slow handler would otherwise stall every
other event and delay every response, including the ones the same application is awaiting.

## Consequences

- Handler order is not a guarantee. Two handlers for the same event run concurrently, and a slow
  handler does not hold up the next frame, so handlers must not assume they finished before the
  next one started.
- Failures are invisible at the call site: a `raise` inside a handler produces a hook call, not an
  exception in `run()`. Without an `on_handler_run_failed` handler the exception is dropped.
- `stop()` does not cancel in-flight handlers; a handler still running when the application exits
  is the application's problem.
- There is no backpressure: a handler that lags behind the event rate accumulates tasks instead of
  slowing the stream.
