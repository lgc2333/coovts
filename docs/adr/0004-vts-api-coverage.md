# Model the stable VTube Studio API one to one, and nothing else

**Status**: accepted

The request and event models mirror the stable, documented VTube Studio plugin API one to one:
35 of the 37 requests in the official README are modelled, plus the 10 documented events, with
class names matching the documented `messageType` values and field names matching the documented
payload keys. Two categories are deliberately not modelled — endpoints that exist only on VTS's
public beta branch, and API surfaces that are not a request/response message pair at all.

## Consequences

- `ArtMeshAtPosition` (beta-only) is absent on purpose: following it would couple the model set to
  a branch that can change without a stable version bump. `ItemSort` is stable but simply not
  written yet.
- The permission flow is unimplemented, so a plugin cannot ask VTS in advance whether a call will
  be allowed; a refused call surfaces as an API error at call time.
- UDP discovery is unimplemented, so the endpoint is configured by hand instead of discovered on
  port 47779.
- The unsolicited `VTubeStudioAPIStateBroadcast` is unmodelled. VTS broadcasts it over UDP on port
  47779, which the library never listens on, so it cannot reach a plugin at all; a frame of that
  type sent over the WebSocket by hand would decode as an ordinary envelope and then be dropped like
  any other frame with no handler and no matching request.

The permission flow, UDP discovery and `ItemSort` are "not yet" rather than "never": each of them
becomes worth doing when a real plugin needs it, and until then a half-modelled surface would be
worse than an absent one.
