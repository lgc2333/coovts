# The typed API surface is a generated stub beside an untyped ABC

**Status**: accepted

`PluginAPI` is an ABC with two untyped abstract seams (`_call_api`, `_handle_event`) and two
untyped public forwarders (`call_api`, `handle_event`). `Plugin` implements the seams and inherits
the forwarders, so the runtime carries no per-request code; all typing lives in
`coovts/types/plugin_api.pyi`, generated from the request and event models by
`scripts/generate_plugin_api.py` (one typed `call_api` overload per request and one typed
`handle_event` overload per event, plus a generic one each; the counts live in
`docs/references.md`).

Writing every overload by hand in the runtime class would be code that can disagree with the models
it describes. Generating the stub from the models means the type surface cannot drift from what the
runtime resolves, and the runtime stays small enough to read in one sitting.

## Consequences

- The stub is derived state: regenerate it with `poe gen-api` after touching `types/api` or
  `types/event`, and never edit it by hand.
- Generation walks the `api` and `event` package namespaces, so a new model module that is not
  re-exported from the package `__init__` produces no overload *and* is unresolvable at runtime
  (see ADR-0001).
- Drift is a red build, not a user's surprise: the generator has a `--check` mode that renders the
  stub in memory and fails on any difference from the file on disk, and CI runs it on every push.
  It writes atomically for the same reason — a crash halfway through rendering must not leave a
  truncated stub behind.
