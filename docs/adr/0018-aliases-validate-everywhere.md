---
status: accepted
amends: ['0014']
amended_by: ['0020']
---

# Aliases validate everywhere, not only where a frame enters

Every payload model inherits `VTSBaseModel`, whose only job is `vts_base_model_config`: camelCase
aliases generated from the field names, `validate_by_name=True`, `validate_by_alias=True` and
`serialize_by_alias=True`. Both spellings validate anywhere — the python field name for code that
builds a payload, the wire alias for a frame that arrives — and only the wire spelling goes out.

ADR-0014 kept the alias half of validation opt-in instead: the config said
`validate_by_alias=False`, and the three places a frame enters asked for aliases by hand with
`by_alias=True`. That flag bought less than it looked. Pydantic turns `validate_by_name` on by itself
when `validate_by_alias` is off, so every boundary call already accepted field names as well, and
there was never a call site where a wire spelling worked and a field name did not. What the flag
marked was the reader's intent — this data came off the wire — which is a fact about where data came
from rather than about which keys are legal. The library now says the policy once, in the config, and
`Plugin._handle_raw` and `PendingRequest.result` validate without a flag.

Alternatives rejected:

- **Keep names-only validation and the per-call flag.** The strictness lives in a mode each call site
  has to remember rather than in the payload, and the flag was not even strict: the boundary accepted
  field names too. All it still prevented was building a model from a wire key by accident, which is
  what a plugin hand-decoding a payload it did not model wants to do.
- **`populate_by_name=True`.** The pre-2.11 spelling of the same idea, and it states only half of what
  the config now states: names validate; whether aliases do is left to the other default. One field,
  one policy, in the current vocabulary.

## Consequences

- The three `by_alias=True` call sites are gone. `model_validate` behaves the same at every call site,
  so a frame and a python dict both decode anywhere; ADR-0014's "reading a frame is a deliberate step"
  goes with them, leaving the boundary itself — a websocket receive and a response lookup — as what
  marks wire data.
- `ModelLoadRequest.model_validate({"modelID": "m1"})` and `ModelLoadRequest(model_id="m1")` are now
  equivalent, where the first used to be an error. The alias keyword itself works at runtime and
  still fails a type check: pydantic's constructor signature is generated from the field names, so
  basedpyright reports `modelID` as an unknown argument. Python code therefore keeps writing field
  names, and the alias stays what the wire speaks — enforced by the type checker instead of by the
  validator.
- A field's alias may not collide with another field's name in the same model, or one key would feed
  two fields. No model has such a pair (checked across the 143 models the packages declare), and the
  only way to write one is a mixedCase field name, which ruff's `N815` rejects.
- Serialization is untouched: dumps spell fields the way the wire does, nested models included, so a
  request holding a response model still goes out with the aliases of both.
