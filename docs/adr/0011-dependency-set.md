# Dependencies: Pydantic for the wire, websockets for transport, loguru optional

**Status**: accepted

The runtime dependency set is three packages, each with one job: Pydantic v2 defines and validates
every wire model, `websockets` is the transport, and `cookit` supplies `model_with_model_config` and
`warning_suppress`. Logging is the one thing that does not have to be there: `loguru` lives in the
optional `log` extra (which also pulls `cookit[loguru]`), and `coovts/log.py` imports it lazily and
falls back to a no-op logger when it is missing. There are no version ceilings.

Pydantic is not just a convenience here: the wire layer's behaviour _is_ Pydantic's behaviour. The
asymmetric validation policy of ADR-0002 and the wholesale config injection of ADR-0003 are
Pydantic v2 features (`validate_by_alias`, `serialize_by_alias`, `ConfigDict` inheritance), and the
models are the public type surface users read in their editor.

A plugin author already runs an application with its own logging setup: a library that forces a
logger into their process decides for them, and a hard dependency on one turns "coovts is
installed" into "loguru is installed". The extra keeps the diagnostics available to whoever wants
them without making silence cost anything.

## Consequences

- `pip install coovts` imports and runs without `loguru`. `coovts/log.py` must keep degrading
  gracefully: its import-guard branch is dependency-gated and therefore exempt from coverage.
- Diagnostics are silently dropped in that configuration, so anything the library wants a user to
  see has to reach them another way — a hook or an exception, never only a log line.
- The transport is used with its defaults: keepalive interval, frame size limit and close timeouts
  are not configurable through `Plugin`, so an application that needs different values must go
  around the library.
- The Pydantic v2 floor propagates to users: their environment must already accept v2, and the
  Pydantic v1 spellings of the same settings do not apply.
