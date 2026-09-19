---
status: accepted
amends: ['0007']
amended_by: ['0021']
---

# The run owns the session, and a drop ends it quietly

ADR-0007 gives the plugin one supervisor task that connects, authenticates and then receives until
the socket fails. The receiving half is a task of its own, and the supervisor parks on it: for the
run, "the receive loop ended" means "the session is over, connect again". Every disconnect went
through `_disconnect`, which cancelled that task. So a caller who asked for a fresh session — the
old public `reconnect()` — cancelled the very task the run was parked on and ended the run: no
error, no hook, state stuck on `AUTHENTICATING`, and no attempt to reconnect ever again. The same
cancel was why two concurrent calls could open two sockets, since `_disconnect` rewrites the state
before it yields and the `CONNECTING` guard read exactly that state.

A session is now identified by `Plugin._session`, a counter that every disconnect bumps. The
receive loop captures the counter it was started with, and classifies what ends it: a cancel whose
session is no longer the live one is a disconnect the plugin asked for, so the loop returns quietly
— no `on_connection_closed`, no wait — and the run parked on it survives and opens the next session;
anything else (a socket failure, or a cancel while its session is still current) is reported or
propagated exactly as before. The wait for `reconnect_delay` after a real drop stays inside the
loop, so cancelling the loop is also what makes a drop that is still waiting out its delay retry at
once.

`reconnect(*, wait_connect=False)` is therefore a request, not an action: with a run in progress it
only drops the current session and the run connects and authenticates the next one, and without a
run it connects itself, with nothing supervising it afterwards. It never raises while a run is in
progress, a call that arrives while a connect is already in flight does nothing — that connect is
what it asked for — and `wait_connect` waits for the new socket, not for authentication, giving up
when the run ends. The run's own connect step, previously the public `reconnect()`, is now the
private `_open_session()`, and one lock makes "connect" and "drop" take turns, which is what the
old state guard tried and failed to do.

## Consequences

- `on_connection_closed` means the socket failed. A disconnect the plugin performs itself — a
  caller's `reconnect()`, the teardown after a fatal authentication refusal, `stop()` — no longer
  reaches it, which is what ADR-0016 already wanted for its own teardown; a close that fails reaches
  `on_disconnect_failed`.
- A drop that lands while the run is authenticating is not an authentication failure: the run
  compares the session it opened with the live one and simply opens the next, so
  `on_authenticate_failed` does not fire for a session somebody replaced.
- `stop()` disconnects before it sweeps the handler tasks, so handlers a drop dispatches in that
  window are cancelled with the rest instead of escaping the sweep — and that sweep runs even when
  the close fails, which is a `finally` around the disconnect.
- The run ends through cancellation in the ordinary case (`stop()` cancels it, which cancels the
  receive loop it is parked on); a drop only ends the loop.

Alternatives rejected: keeping `reconnect()` as "connect now" and warning callers off it, which
leaves a method whose only safe use is inside the library; letting the caller's `reconnect()` open
the session itself with the run still running, which gives a session two owners — the run's parked
`await` returns, so it tears down what the caller just opened and connects again; and refusing the
call while a run is going, which cannot express "drop this session now, I know something the socket
does not".
