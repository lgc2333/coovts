# Model the documented VTube Studio API one to one

**Status**: accepted

The request and event models mirror the documented VTube Studio plugin API one to one: all 37
requests of the official API README are modelled, plus the `EventSubscription` pair (documented in
the event reference rather than the request list) and 10 of the 16 documented events. Class names
match the documented `messageType` values wherever the name conventions can produce them, and field
names match the documented payload keys.

Beta-only endpoints are modelled too and say so in their docstring (`ArtMeshAtPosition`). A plugin
whose feature only exists on the beta branch has no other way to reach it, and a clearly marked
endpoint costs a reader less than an absent one — the coupling to a branch that can change without a
stable version bump is a documented risk, not a reason to leave the gap.

Two surfaces stay out of the model set: everything that is not a request/response message pair
(UDP server discovery, the UDP `VTubeStudioAPIStateBroadcast`), and the permission flow, which is
"not yet" rather than "never" — it becomes worth doing when a real plugin needs it.

## Consequences

- Six documented events are missing: `ArtMeshOutlineEvent`, `ArtMeshTrackingEvent`,
  `BackgroundChangedEvent`, `ExpressionToggledEvent`, `ModelConfigChangedEvent` and
  `PostProcessingEvent`. They were never written rather than deliberately left out, so subscribing
  to one is not expressible through the typed surface — only by hand through `call_api`.
- `ArtMeshAtPosition` follows the beta branch, so a change there is a change to a model the library
  ships without a version bump of its own. Against a stable VTS 1.35.10 the request is answered with
  `APIError` id 7 (`Unknown messageType`), which is what the beta marking warns a caller about.
- The permission flow is unimplemented, so a plugin cannot ask VTS in advance whether a call will be
  allowed; a refused call surfaces as an API error at call time.
- UDP discovery is unimplemented, so the endpoint is configured by hand instead of discovered on port
  47779. The unsolicited `VTubeStudioAPIStateBroadcast` is likewise unmodelled: VTS broadcasts it
  over UDP, which the library never listens on, so it cannot reach a plugin at all; a frame of that
  type sent over the WebSocket by hand would decode as an ordinary envelope and then be dropped like
  any other frame with no handler and no matching request.
