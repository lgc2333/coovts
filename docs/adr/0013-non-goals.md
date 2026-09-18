# Non-goals

**Status**: accepted

The library models the API surface recorded in `docs/references.md` and stops where a plugin's
needs stop. The following are deliberate exclusions, not gaps waiting to be filled; each one is
already argued in the ADR that made the decision.

- Python below 3.12 is unsupported, and there is no compatibility shim for an older interpreter
  (ADR-0010).
- There is no synchronous façade over the async core; `run_sync` is the only bridge for blocking
  code (ADR-0010).
- Older VTS API versions are not supported: the library targets the current API and does not probe
  for capabilities or degrade against a pre-`1.0` VTS.
- VTS state is not mirrored locally. Model and item lists, parameter values and event subscriptions
  are asked for when needed; the connection state machine is the only state the library keeps.
- In-flight requests are not retried or resumed across a disconnect; a lost call fails and the
  caller decides whether it is worth repeating (ADR-0008).
- Event handlers get no ordering and no backpressure guarantees: each one runs as its own task, and
  nobody waits for it (ADR-0006).

UDP server discovery and the unsolicited UDP `VTubeStudioAPIStateBroadcast` are absent from this list
on purpose: they are not excluded by a decision, they are simply not built yet. See ADR-0004.
