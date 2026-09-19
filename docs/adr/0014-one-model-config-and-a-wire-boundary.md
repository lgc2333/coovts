---
status: accepted
supersedes: ['0002']
amends: ['0003', '0012']
amended_by: ['0018']
---

# One model config, and a wire boundary that asks for aliases

Every payload model inherits `VTSBaseModel`, whose only job is `vts_base_model_config`: camelCase
aliases generated from the field names, `validate_by_alias=False` and `serialize_by_alias=True`.
One config for the whole library replaces the request/response pair ADR-0002 introduced, so the
direction a payload travels no longer decides how its model is configured.

`validate_by_alias=False` keeps the python field name the only way to build a model, so requests
are written the way the rest of the code reads them (`ModelLoadRequest(model_id="m1")`), and
`serialize_by_alias=True` makes every dump spell fields the way the wire does, nested models
included. That second half is what keeps a request holding a response model honest: the tracking
config embeds the shared `ArtMeshHitInfo`, and it goes out with `artMeshCoords: {modelID,
artMeshID, vertexID1, …}` without a serializer of its own.

Frames from VTube Studio are camelCase, so reading one is a deliberate step that asks for aliases
by hand — `model_validate(data, by_alias=True)` in `Plugin._handle_raw` (the envelope and every
event payload) and in `PendingRequest.result` (the answer to a call). Reading stays guarded the way
ADR-0003 wants it: unknown fields are ignored, and a payload that does not decode is reported
rather than guessed at.

## Consequences

- `with_request_model_config`, `with_response_model_config`, `request_model_config` and
  `response_model_config` are gone; a model is a `VTSBaseModel` subclass, which is also the shape
  pydantic documents. ADR-0012's public surface for `coovts.types.shared` therefore reads
  `VTSBaseModel` and `vts_base_model_config` where it named those config helpers.
- Building a payload from its wire keys, or validating one by hand, now needs `by_alias=True`; the
  three boundaries above are where the library passes it. Field names still work there too, since
  the config accepts them, which costs nothing: VTube Studio only ever sends aliases.
- The configs no longer come from a `cookit` factory, so the dynamically created subclass behind
  every model — and the class metadata pydantic could not keep for it — is gone with them.
- A model may still set its own `model_config`; pydantic merges it key by key over
  `vts_base_model_config`, so an override adds a key instead of dropping the aliases.
