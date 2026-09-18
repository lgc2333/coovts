# Wire names are derived from class names

**Status**: accepted

Every wire string is computed from a Python class name instead of living in a registry or a tagged
union: `get_message_type` returns the class name verbatim (the model `AuthenticationRequest` *is*
the `messageType`), `get_api_response_model` maps `XRequest` to `XResponse`, and `get_event_name`
maps `XEventData`/`XEventConfig` to `XEvent`. Adding one API therefore means writing one model and
nothing else, and there is no second list that can drift out of sync with the API surface we model
(see `docs/references.md`).

## Consequences

- Class names are part of the wire protocol. Renaming `ModelMovedEventData` silently changes the
  event name plugins subscribe to, so such a rename is a breaking change even though it reads like
  a refactor.
- `msg_t`, `resp_t` and `resp_m` are per-model escape hatches for names the conventions cannot
  produce. No model uses them today; they exist so an awkward name bends the convention instead of
  breaking it.
- The conventions are checked by nothing but their own use: the generator and the runtime resolver
  both walk the `api`/`event` packages, so a model that is not re-exported from the package
  `__init__` is invisible to both, and the failure shows up as a `ValueError` at call time.

The alternatives — an explicit registry keyed by message type, or a Pydantic discriminated union —
would each store the same mapping in a second place, and a second place can disagree with the
models. The union was never viable anyway: a response's type is a property of the request we sent,
not of the frame, so the discriminator would still have to be threaded through at runtime.
