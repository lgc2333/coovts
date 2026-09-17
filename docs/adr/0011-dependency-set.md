# Dependencies: Pydantic for the wire, websockets for transport, loguru and cookit

**Status**: accepted

The runtime dependency set is four packages, each with one job: Pydantic v2 defines and validates
every wire model, `websockets` is the transport, `loguru` is the logging used by the library's own
diagnostics, and `cookit` supplies `model_with_model_config` and `warning_suppress`. There are no
optional extras and no version ceilings.

Pydantic is not just a convenience here: the wire layer's behaviour *is* Pydantic's behaviour. The
asymmetric validation policy of ADR-0002 and the wholesale config injection of ADR-0003 are
Pydantic v2 features (`validate_by_alias`, `serialize_by_alias`, `ConfigDict` inheritance), and the
models are the public type surface users read in their editor.

## Consequences

- The transport is used with its defaults: keepalive interval, frame size limit and close timeouts
  are not configurable through `Plugin`, so an application that needs different values must go
  around the library.
- `loguru` is both a direct dependency and an extra of `cookit`, so it reaches the environment
  twice; a caller who configures logging configures both appearances.
- The Pydantic v2 floor propagates to users: their environment must already accept v2, and the
  Pydantic v1 spellings of the same settings do not apply.
