# Changelog

English | [简体中文](CHANGELOG.zh-cn.md)

Releases are listed newest first, with the PyPI upload dates. On the `0.0` line nothing was promised
and the number said nothing about the size of a change; from `0.1` on, the minor is where breaks live
([ADR-0012](./docs/adr/0012-public-api-and-versioning.md)).

## 0.1.0 (unreleased)

Leaves the `0.0` unstable line: the version number now says what a release does, and the package
metadata drops the alpha status (ADR-0012). Everything below landed after `0.0.1.alpha2` and is not
on PyPI yet.

- Transcribed the upstream constant tables — error IDs, hotkey actions, effects and their configs,
  restricted keys — into `coovts.types.consts`.
- Modelled the permission flow, the six events that were missing, `ItemSort`, and the ArtMesh models
  shared between the api and event packages.
- Replaced the per-model config decorators with one base model and one config dict,
  `VTSBaseModel` / `vts_base_model_config`.
- An authentication refusal a retry cannot fix now ends the run instead of looping, and `stop()`
  cancels the handler tasks still in flight.
- A lost connection fails pending requests with `NetworkError`, and a request past its deadline
  raises `RequestTimeout`.
- Logging is optional: `loguru` is no longer a hard dependency.
- `call_api` and `handle_event` are generated into a stub from the models, with CI failing on drift.
- Added a pytest suite replayed against frames captured from a real VTube Studio.
- Added `CONTEXT.md`, the ADRs, the user guide, and this changelog.

## 0.0.1.alpha2 — 2025-05-21

- Refactored the project, completed the missing data models, and made the type hints better.

## 0.0.1.alpha1 — 2025-04-11

- First alpha release.
