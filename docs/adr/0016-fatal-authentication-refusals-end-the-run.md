---
status: accepted
---

# Authentication refusals a retry cannot fix end the run

A token request reaches the user as a popup in VTube Studio, and some answers do not change however
often it is asked: the user denied it, the plugin's name, developer or icon is rejected as invalid,
or the request and the token it carries are malformed. The reconnect loop of ADR-0007 would answer
those by reconnecting and asking again, so a denial means re-opening the popup every
`reconnect_delay` with `stop()` as the only way out. Against a live VTS that refusal is
`APIError[50] User denied authentication request for your plugin.`

`Plugin._run` therefore reads the error ID of a failed authentication against the private
`_FATAL_AUTH_ERROR_IDS`, and a match ends the run: the `on_authenticate_failed` handlers still see
the failure first, the plugin disconnects, and its state settles on `STOPPED` — "not connected and
not trying" — instead of `DISCONNECTED`, which means the reconnect loop is still at work. The state
is set before the disconnect precisely so the disconnect does not read as a connection loss. `run()`
returns, and a caller that disagrees can start another run on its own.

The set is the refusals a retry cannot fix: `APIAccessDeactivated`, `JSONInvalid`, `APINameInvalid`,
`APIVersionInvalid`, `TokenRequestDenied`, `TokenRequestPluginNameInvalid`,
`TokenRequestDeveloperNameInvalid`, `TokenRequestPluginIconInvalid`, `AuthenticationTokenMissing`,
`AuthenticationPluginNameMissing`, `AuthenticationPluginDeveloperMissing`. Two neighbouring IDs are
deliberately outside it: `TokenRequestCurrentlyOngoing` (51) means the popup is open right now and
the answer is still coming, and `RequestIDInvalid` (5) is about one attempt's envelope, while the
next attempt carries a fresh id. Everything else — a dead socket, a refused connection, any other
`APIError` — stays in the fixed-delay loop.

The set is a judgement about a user sitting in front of that popup, not an upstream fact, which is
why it lives privately in `plugin.py` rather than in `coovts/types/consts/`, where transcriptions
keep upstream verbatim (ADR-0015). The alternatives were to keep retrying regardless, either with a
longer delay or with the hook deciding: a plugin author knows nothing the error ID does not already
say, and a slower loop still asks a user who has already said no.
