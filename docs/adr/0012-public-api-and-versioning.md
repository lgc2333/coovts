# Everything without a leading underscore is public, and nothing is promised before 1.0

**Status**: accepted

The public API is every symbol the package exposes that does not start with an underscore — the
`Plugin` class and its hooks, the models in `coovts.types.api` and `coovts.types.event`, the
name-convention resolvers and config helpers in `coovts.types.shared`, the exception classes in
`coovts.errors`, and the generated type surface of `call_api` / `handle_event`. A leading
underscore is the only marker of "internal", and it is load-bearing. Class names in the wire
packages are public too, because they *are* the protocol (ADR-0001).

While the version is `0.0.x`, compatibility is not promised for any of it: a release may break any
public symbol, and the README changelog is the only notice. The version is declared exactly once,
in `coovts/__init__.py`, because the build reads it from there.

## Consequences

- Users must pin a version; "latest 0.x" is not a safe constraint.
- Additive changes still deserve a release note: the pre-1.0 policy permits breakage, it does not
  make breakage invisible.
- The alpha suffix marks release confidence, not API stability — an alpha and a plain `0.0.x`
  promise the same thing, which is nothing.
