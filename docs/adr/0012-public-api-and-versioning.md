# Everything without a leading underscore is public, and `0.0` means unstable

**Status**: accepted

The public API is every symbol the package exposes that does not start with an underscore — the
`Plugin` class and its hooks, the models in `coovts.types.api` and `coovts.types.event`, the
name-convention resolvers, `VTSBaseModel` and `vts_base_model_config` in `coovts/types/shared.py`,
the exception classes in `coovts.errors`, and the generated type surface of `call_api` /
`handle_event`. A leading underscore is the only marker of "internal", and it is load-bearing. Class
names in the wire packages are public too, because they _are_ the protocol (ADR-0001).

The version is declared exactly once, in `coovts/__init__.py`, because the build reads it from there.
`0.0` is the unstable line: while the version is `0.0.x` nothing is promised — the number inside it
says nothing about what a release did, any public symbol may break, and `CHANGELOG.md` is the only
notice. The unstable line ends at `0.1`, not at `1.0`.

From `0.1` on, the number says what a release does: a big refactor bumps the major, a breaking change
or a big feature bumps the minor, a fix bumps the patch. The scheme follows the frontend habit of
spending majors on rewrites rather than on every break, so the promise starts at `0.1` rather than at
`1.0` — and a patch release is the only one that is always safe to take.

## Consequences

- Users pin a version. While `0.0.x` is unstable nothing constrains a release at all, and from `0.1`
  on the minor is where breaks live, so "latest 0.x" is never a safe constraint.
- Additive changes still deserve a release note: permitting breakage does not make breakage invisible.
- The alpha suffix marks release confidence, not API stability — an alpha promises exactly what the
  same version without it promises.
