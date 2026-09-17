# Request correlation, timeouts, and which failures are exceptions

**Status**: accepted

Each outbound request is registered in a table under a decimal-string id (`"1"` … `"2147483647"`,
wrapping and skipping ids already in flight), sent with that id in the envelope, and awaited as a
future that the receive loop resolves when a frame with the matching id arrives. A response is
consumed exactly once: the table entry is popped on match and discarded afterwards, so a late
duplicate is dropped. The default timeout is 30 seconds; `0` and `None` both mean "wait forever".

Only request-scoped failures are exceptions. `ValidationError` (the payload did not decode to the
expected model) and `APIError` (VTS refused the request) are raised at the `await`; connection
loss, envelope parse failures, connect failures, authentication transport failures and handler
crashes are reported through hooks instead. That split is the reason there is no exception type for
a lost connection and no `on_disconnected` callback.

## Consequences

- A disconnect cancels every pending request, so an awaited call raises `asyncio.CancelledError`
  rather than a `VTSError` subclass. The library does not retry or re-send: the caller decides
  whether a lost call is worth repeating.
- `api_timeout=0` means "forever" rather than "immediately" — a deliberate special case, since a
  caller who wants no deadline should not have to say `None` differently from `0`.
- The id counter is per connection and resets on disconnect; ids are never reused within a
  connection but say nothing across connections.
