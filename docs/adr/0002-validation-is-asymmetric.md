---
status: superseded
superseded_by: ['0014']
---

# Requests validate by field name, responses by wire alias

Request models set `validate_by_alias=False` together with `serialize_by_alias=True`: user code
builds them with snake_case keywords, and a plain `model_dump_json()` emits camelCase without
anyone passing `by_alias=True`. Response models keep Pydantic's defaults and therefore validate
camelCase only. Constructing a request is a pure Python act where the wire spelling never appears,
while decoding an inbound payload is strict about the wire spelling — a `model_loaded` key arriving
from VTS is an error rather than a silently accepted alias.

## Consequences

- Aliases on requests exist for serialization only; passing an alias by keyword does not work.
- The same request config decorates the event config models, which also travel outbound, so the
  split is "outbound is snake_case in Python" rather than "requests are snake_case".
- The two policies live in `types/shared.py` and nowhere else; a model that declines the decorator
  is a model with different wire behaviour.
