---
status: accepted
amends: ['0019']
---

# A connect has an owner, and only a live session reaches the hooks

ADR-0019 made the run the owner of the session, with one exception: a `reconnect()` with no run in
progress connects by itself, and nothing supervises it afterwards. That connect belonged to the
caller rather than to the plugin, and every hole it left came from the same place.

`reconnect(*, wait_connect=False)` now owns the connect it starts: the plugin runs it as a task of
its own, keeps it in `Plugin._connect_task`, and every caller of that connect awaits the same task. A
`wait_connect=True` call that lands while a connect is in flight therefore waits for the outcome of
that connect and gets the failure the first caller gets — it no longer waits on a signal that a
failed connect never sets.

`stop()` is final for `reconnect()`. It sets `Plugin._shut_down`, which only `run()` clears, and a
call on a plugin that was shut down raises `RuntimeError` instead of opening a session nobody asked
for. A run that ended on a fatal authentication refusal sets the same latch, since ADR-0016 already
says such a run ends and only `run()` starts another. The same latch is what a connect already in
flight is checked against: `_open_session` closes the socket it just opened instead of adopting it
when the plugin was stopped while that connect ran, since the socket has no owner left. `stop()` also
cancels the connect it owns before it disconnects, so nothing lands behind it.

Ownership is what `stop()` forgets, and only what it owns: it clears `Plugin._run_task` when the record
is still the run it cancelled, so a `run()` that started while the stop was unwinding stays reachable —
and reachable is what a later `stop()` needs.

`stop()` is safe to call from inside a hook or a handler: the task making the call is left out of the
handler sweep, because cancelling it would cancel the gather that cancels it.

A session is live only while its socket is, and a hook sees only a live session. `authenticate()`
captures the `(session, client)` pair it started with and refuses to dispatch `on_authenticated` once
that pair no longer describes the live session: a drop while the declared events are being re-sent
means the socket this authenticated is gone, and per-session setup in the hook would run against it.
The pair is what sees it, because a drop bumps nothing — `_disconnect` is what bumps the session
counter, and a receive loop that ends on its own is not a disconnect — while the socket's own close
state is what a drop leaves behind. `Plugin._run` keeps classifying a failed authentication by the
counter and by the error it got, so a drop during the handshake reconnects instead of reaching
`on_authenticate_failed`, and a refusal VTS answered still reaches it, fatal or not (ADR-0016).

## Consequences

- `reconnect(wait_connect=True)` without a run returns when the socket is up, or raises what the
  connect raised. With a run in progress the wait is still the `connected` event, and it still gives
  up when the run ends.
- A `RuntimeError` from `reconnect()` is how a caller learns that the plugin it was reconnecting is
  stopped; no new exception type carries that.
- `stop()` twice stays harmless, and `run()` after `stop()` still starts the plugin again from the top.
- Pending requests are untouched by all of this: a disconnect fails them with `NetworkError`, except
  for `stop()`, which cancels them (ADR-0008).
- A request whose `send` fails after the disconnect already failed it takes that exception off the
  future, so the loop has nothing to log and ADR-0011 keeps holding.

Alternatives rejected: keeping the caller as the owner of the connect and making `stop()` wait for it,
which makes a stop as slow as a connect to an endpoint that never answers; adopting the socket a
stopped plugin just opened only to close it again, which reports `on_connected` and starts a receive
loop for a session the plugin may not have; and comparing the session counter alone before the hook,
which cannot see a drop at all.
