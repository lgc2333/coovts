# Model the documented VTube Studio API one to one

**Status**: accepted

The request and event models mirror the documented VTube Studio plugin API one to one: every
request of the official API README is modelled, plus the `EventSubscription` pair (documented in
the event reference rather than the request list) and every documented event. Class names match the
documented `messageType` values wherever the name conventions can produce them, and field names
match the documented payload keys. The current counts are recorded in `docs/references.md`.

Beta-only endpoints and events are modelled too and say so in their docstring (the
`ArtMeshAtPosition` request, the `ExpressionToggledEvent`, `ArtMeshTrackingEvent` and
`ArtMeshOutlineEvent` events). A plugin whose feature only exists on the beta branch has no other
way to reach it, and a clearly marked endpoint costs a reader less than an absent one — the
coupling to a branch that can change without a stable version bump is a documented risk, not a
reason to leave the gap.

One surface stays out of the model set: everything that is not a request/response message pair —
UDP server discovery and the unsolicited UDP `VTubeStudioAPIStateBroadcast`.

## Consequences

- `ArtMeshAtPosition` follows the beta branch, so a change there is a change to a model the library
  ships without a version bump of its own. Against a stable VTS 1.35.10 the request is answered with
  `APIError` id 7 (`Unknown messageType`), and the three beta events the same way with id 950
  (`Unknown API event type`) — which is what the beta marking warns a caller about.
- UDP discovery is unimplemented, so the endpoint is configured by hand instead of discovered on port
  47779. The unsolicited `VTubeStudioAPIStateBroadcast` is likewise unmodelled: VTS broadcasts it
  over UDP, which the library never listens on, so it cannot reach a plugin at all; a frame of that
  type sent over the WebSocket by hand would decode as an ordinary envelope and then be dropped like
  any other frame with no handler and no matching request.
