# Changelog

English | [简体中文](CHANGELOG.zh-cn.md)

The newest release is first. Its date is the PyPI upload date.

## 0.1.0 (unreleased)

This release leaves the unstable `0.0` line. The version number now says what a release does, and the
package metadata no longer declares the alpha status (ADR-0012). Every item below came after
`0.0.1.alpha2`, and no item is on PyPI yet.

- `coovts.types.consts` now holds the upstream constant tables: error IDs, restricted keys, hotkey
  actions, and post-processing effects with their configs.
- The library gains the permission flow, the six events that were missing, `ItemSort`, and the
  ArtMesh models that the api package and the event package share.
- One base model and one config dict replace the per-model config decorators: `VTSBaseModel` and
  `vts_base_model_config` ([ADR-0014](./docs/adr/0014-one-model-config-and-a-wire-boundary.md)).
- Every payload model now validates by field name and by wire alias. A frame and a Python dict both
  decode at any call site, and no call site passes `by_alias=True` any more
  ([ADR-0018](./docs/adr/0018-aliases-validate-everywhere.md)).
- A fatal authentication error now ends the run. A refusal that a retry cannot fix is not retried
  ([ADR-0016](./docs/adr/0016-fatal-authentication-refusals-end-the-run.md)).
- `stop()` cancels the handler tasks that are still running.
- A lost connection fails every pending request with `NetworkError`.
- A pending request that passes its API timeout raises `RequestTimeout`.
- The library does not log. The logging shim, the `log` and `all` extras, and the `cookit`
  dependency are gone ([ADR-0011](./docs/adr/0011-dependency-set.md)).
- A disconnect that the plugin starts itself now reports a failed close to the new
  `on_disconnect_failed` hook.
- `Plugin.stopped` is gone. The supervisor stops when a caller cancels it, so a caller stops the
  plugin with `await plugin.stop()` and reads the state from `plugin.state`.
- The generated API surface now covers `call_api` and `subscribe_event`, typed per model. CI fails
  when the stub and the models disagree. `handle_event` is a generic method on `Plugin`.
- A pytest suite replays frames that a real VTube Studio captured.
- `CONTEXT.md`, the ADRs, the user guide, and this changelog are new.
- `plugin.subscribe_event(...)` declares an event once. The declaration holds the data model, the
  config of its subscription, and its handlers. The library sends the subscription again after every
  reconnect, so a subscription cannot stay lost
  ([ADR-0017](./docs/adr/0017-declared-events-are-resubscribed.md)).
- The call hands back a wrapped handler that carries `dispose()`. A caller that awaits the call
  subscribes at once.
- An event can also be named by its wire name. Then the library decodes nothing, and the handler
  gets the raw payload.
- A subscription that VTS refuses now reaches the new `on_subscribe_failed` hook. It no longer fails
  the authentication.
- The generated stub gives `subscribe_event` one typed overload per event. The `config` argument is
  optional only when the event config model has no required field.

## 0.0.1.alpha2 — 2025-05-21

- This release refactored the project, completed the missing data models, and improved the type
  hints.

## 0.0.1.alpha1 — 2025-04-11

- First alpha release.
