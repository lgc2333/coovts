# Model config is injected wholesale, and unknown fields are ignored

**Status**: accepted

No model declares its own `model_config`. Config arrives through `with_request_model_config` /
`with_response_model_config`, a `cookit` factory that returns a same-named subclass of the
decorated class with the config dict set as a whole and nothing merged from a parent. `extra` is
never set by anyone, so Pydantic's default `extra="ignore"` applies to all 120 models.

The tolerant reader is a protocol requirement, not politeness: VTube Studio documents that new
fields can appear in existing payloads without a version bump, so an inbound frame carrying a field
we do not know must be decoded, not rejected.

## Consequences

- Unknown inbound fields are dropped silently. A new VTS field is invisible until we model it.
- Adding one setting to a policy means restating the whole policy in `types/shared.py`; a decorated
  model cannot be subclassed to override a single setting, because the config dict is replaced
  wholesale.
- The decorators are invisible at the type level: a decorated class is a same-named subclass, so
  `type(model).__name__` and reprs look untouched while the class object is not the one written in
  the source file.

The alternatives were per-model `model_config` (120 copies of one policy that must be edited in
lockstep) and a shared `BaseModel` subclass carrying the config (a library-owned base class in
every model's MRO, and two parallel hierarchies for the request and response halves).
