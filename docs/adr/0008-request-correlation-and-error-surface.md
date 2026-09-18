# Request correlation, timeouts, and which failures are exceptions

**Status**: accepted

Each outbound request is registered in a table under a decimal-string id (`"1"` … `"2147483647"`,
wrapping and skipping ids already in flight), sent with that id in the envelope, and awaited as a
future that the receive loop resolves when a frame with the matching id arrives. A response is
consumed exactly once: the table entry is popped on match and discarded afterwards, so a late
duplicate is dropped. The default timeout is 30 seconds; `0` and `None` both mean "wait forever".

Only request-scoped failures are exceptions. `ValidationError` (the payload did not decode to the
expected model), `APIError` (VTS refused the request) and `RequestTimeout` (the deadline expired
before the answer arrived) are raised at the `await`, and a request whose connection dies before
the answer arrives fails with `NetworkError` — the same error used when a call is attempted with
no connection. Envelope parse failures, connect failures,
authentication transport failures and handler crashes stay on the hook side, so hooks keep carrying
the transport's own exception (a `ConnectionClosed` still exposes its close code) while `await`
sites only ever see library types. That split is also why there is no `on_disconnected` callback.

## Consequences

- A disconnect fails every pending request with `NetworkError`, and does so the moment the receive
  loop notices — not when the next reconnect attempt starts. The library does not retry or re-send:
  the caller decides whether a lost call is worth repeating.
- `stop()` is the one disconnect that cancels instead of failing, so a shutdown raises
  `asyncio.CancelledError` — the ordinary asyncio signal for "your task is being torn down".
- `api_timeout=0` means "forever" rather than "immediately" — a deliberate special case, since a
  caller who wants no deadline should not have to say `None` differently from `0`.
- `RequestTimeout` subclasses the builtin `TimeoutError` and therefore `OSError`, so `except OSError`
  also catches an expired request — which is why the `client.send()` wrapper in `plugin.py` stays
  narrow: it wraps only the send, never the await of the response.
- The id counter is per connection and resets on disconnect; ids are never reused within a
  connection but say nothing across connections.
