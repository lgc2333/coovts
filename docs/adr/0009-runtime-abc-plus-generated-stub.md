# The typed API surface is a generated stub beside an untyped ABC

**Status**: accepted

`PluginAPI` is an ABC with two untyped abstract seams (`_call_api`, `_handle_event`) and two
untyped public forwarders (`call_api`, `handle_event`). `Plugin` implements the seams and inherits
the forwarders, so the runtime carries no per-request code; all typing lives in
`coovts/types/plugin_api.pyi`, generated from the request and event models by
`scripts/generate_plugin_api.py` (36 typed `call_api` overloads plus 4 generic ones, 10 typed
`handle_event` overloads plus 1 generic one).

Writing 40 overloads by hand in the runtime class would be code that can disagree with the models
it describes. Generating the stub from the models means the type surface cannot drift from what the
runtime resolves, and the runtime stays small enough to read in one sitting.

## Consequences

- The stub is derived state: regenerate it with `poe gen-api` after touching `types/api` or
  `types/event`, and never edit it by hand.
- Generation walks the `api` and `event` package namespaces, so a new model module that is not
  re-exported from the package `__init__` produces no overload *and* is unresolvable at runtime
  (see ADR-0001).
- Nothing verifies the stub against the models: there is no test that regenerates it and compares,
  so drift is caught only when a user's type checker disagrees with the runtime.
