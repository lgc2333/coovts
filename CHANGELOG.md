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
- Payload models now validate by field name and by wire alias everywhere, so a frame and a python dict
  both decode at any call site and nothing passes `by_alias=True` anymore
  ([ADR-0018](./docs/adr/0018-aliases-validate-everywhere.md)).
- An authentication refusal a retry cannot fix now ends the run instead of looping, and `stop()`
  cancels the handler tasks still in flight.
- A lost connection fails pending requests with `NetworkError`, and a request past its deadline
  raises `RequestTimeout`.
- Dropped the logging shim, the `log` / `all` extras and the `cookit` dependency: the library logs
  nothing at all ([ADR-0011](./docs/adr/0011-dependency-set.md)).
- A disconnect the plugin performs on its own reports a refusing close to the new
  `on_disconnect_failed` hook.
- `Plugin.stopped` is gone: the supervisor stops by being cancelled, so `await plugin.stop()` is the
  way to stop it and `plugin.state` is what to read.
- `call_api` and `subscribe_event` are generated into a stub from the models, with CI failing on
  drift; `handle_event` is a generic method on `Plugin`.
- Added a pytest suite replayed against frames captured from a real VTube Studio.
- Added `CONTEXT.md`, the ADRs, the user guide, and this changelog.
- Events are declared once with `plugin.subscribe_event(...)`, which pairs the handler with the
  subscription and re-sends it after every reconnect; the handler it hands back is wrapped and
  carries `dispose()`, and awaiting the declaration subscribes right away. An event may also be named
  by its wire name, in which case nothing is decoded and the handler gets the raw payload.
- A subscription VTS refuses now reaches the new `on_subscribe_failed` hook instead of failing the
  authentication.
- The generated stub gains a typed `subscribe_event` overload per event, whose `config` is only
  optional when its config model has no required field.

## 0.0.1.alpha2 — 2025-05-21

- Refactored the project, completed the missing data models, and made the type hints better.

## 0.0.1.alpha1 — 2025-04-11

- First alpha release.
