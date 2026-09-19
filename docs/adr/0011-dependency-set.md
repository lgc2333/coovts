---
status: accepted
---

# Dependencies: Pydantic for the wire and websockets for transport

The runtime dependency set is two packages, each with one job: Pydantic v2 defines and validates
every wire model, and `websockets` is the transport. There are no version ceilings, and nothing else
— in particular no logging library, because the library does not log.

Pydantic is not just a convenience here: the wire layer's behaviour _is_ Pydantic's behaviour. The
validation policy (build by field name, read by wire spelling, ignore unknown fields) and the one
shared config are Pydantic v2 features (`validate_by_alias`, `serialize_by_alias`, `ConfigDict`
inheritance) recorded in ADR-0014 and ADR-0003, and the models are the public type surface users read
in their editor.

A plugin author already runs an application with their own logging setup, and the library has nothing
of its own to say into it: everything a caller has to know arrives as a hook or an exception, so a
fact that only a log line carries is a fact half the users never see. Should the library ever need
diagnostics of its own, that is a decision of its own to make — and it would be `loguru` rather than
whatever a feature happens to drag in.

## Consequences

- `pip install coovts` installs Pydantic and `websockets`, and nothing else: there are no extras.
- Failure reporting is designed rather than sprinkled. Every failure the library can produce has a
  hook or an exception behind it, so a new failure means adding one of those two, not a log line.
- The transport is used with its defaults: keepalive interval, frame size limit and close timeouts
  are not configurable through `Plugin`, so an application that needs different values must go around
  the library.
- The Pydantic v2 floor propagates to users: their environment must already accept v2, and the
  Pydantic v1 spellings of the same settings do not apply.
