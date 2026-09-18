# When things fail

> [简体中文](../zh-cn/05-failures.md)

## The split: hooks versus `await`

This is the first thing to internalise about the library:

| Where you see the error      | What you see                                                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------ |
| A hook (`on_xxx`)            | The transport's **verbatim exception**, or a library type. A `ConnectionClosed` still carries its close code |
| `await plugin.call_api(...)` | **Only library types**: `APIError` / `ValidationError` / `RequestTimeout` / `NetworkError`                   |

So the `e` in `on_authenticate_failed(e)` may be an `APIError` (VTS decided) or a
`ConnectionClosed` (the socket died). **Telling those apart means checking
`isinstance(e, APIError)` yourself.** Connection-level failures cannot show up at an `await` for a
request, because by then there is no request waiting. A disconnect the library performs on its own is
hook-only in the same way: it reaches `on_disconnect_failed`, never an `await`.

That split is also why there is no `on_disconnected` callback: a dropped connection is already
visible as "every pending request failed with `NetworkError`" plus "`on_connection_closed` got the
transport exception", and a dedicated hook would only add another path to forget to handle.

## Authentication refusals that stop the plugin

Some authentication failures would fail identically a thousand times: VTS has already decided (the
user refused, the request or token is invalid). Those end the supervisor run, leaving the state at
`STOPPED`:

| Error ID | Meaning                      |
| -------- | ---------------------------- |
| 1        | API access deactivated       |
| 2        | JSON invalid                 |
| 3        | API name invalid             |
| 4        | API version invalid          |
| 50       | Token request denied         |
| 52       | Plugin name invalid          |
| 53       | Developer name invalid       |
| 54       | Plugin icon invalid          |
| 100      | Authentication token missing |
| 101      | Plugin name missing          |
| 102      | Plugin developer missing     |

Conversely these do **not** stop it: 51 (the request popup is already open) and 5 (a retry uses a
fresh request ID), plus anything else that a later attempt might get a different answer to. The
reasoning is in [ADR-0016](../../adr/0016-fatal-authentication-refusals-end-the-run.md).

## What is never retried automatically

- **Requests in flight.** A disconnect fails them; a successful reconnect does not re-send them.
  Whether to repeat a lost call is the caller's decision ([ADR-0008](../../adr/0008-request-correlation-and-error-surface.md)).
- **Events.** Lost is lost; VTS does not replay. To converge on the truth, ask again from
  `on_authenticated`.
- **The connection itself** is retried, but only as a fixed-delay reconnect
  ([ADR-0007](../../adr/0007-reconnect-is-a-fixed-delay-loop.md)).

## Not built yet

- UDP server discovery, and the unsolicited `VTubeStudioAPIStateBroadcast`: the endpoint is configured
  by hand. Missing, not excluded ([ADR-0004](../../adr/0004-vts-api-coverage.md)); it is on the
  [backlog](../../backlog.md).

## Things the library deliberately does not do

Deliberate exclusions ([ADR-0013](../../adr/0013-non-goals.md)):

- No local mirror of VTS state (model and item lists, parameter values, subscriptions) — ask when
  you need it.
- No ordering or backpressure guarantees for handlers.
- No API version negotiation: it targets the current API and does not degrade against an older VTS.
- No Python below 3.12, and no compatibility shim for it.

## How to debug, in order

1. `on_connect_failed` / `on_connection_closed` / `on_disconnect_failed` — is the connection layer
   even working? Log the exception as it arrives.
2. `on_recv_raw` / `on_before_send_raw` — the JSON that actually moved.
3. `on_parse_data_error` — frames arrive but do not decode (broken envelope, or payload that does not
   match the model).
4. `on_handler_run_failed` — your own code raised.
5. The library exception at the `await` — the request-level cause; look up `APIError.data.error_id`
   in the ErrorID table.

## Back to the start

[Guide index](./README.md)
