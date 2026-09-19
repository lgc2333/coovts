# Changelog

English | [简体中文](CHANGELOG.zh-cn.md)

The newest release is first. Its date is the PyPI upload date.

## 0.1.0 (unreleased)

### Added

- `coovts.types.consts` now holds the upstream constant tables: error IDs, restricted keys, hotkey
  actions, and post-processing effects with their configs.
- The library gains the permission flow, the events that were missing, `ItemSort`, and the ArtMesh
  models that the api package and the event package share.
- A disconnect that the plugin starts itself now reports a failed close to the new
  `on_disconnect_failed` hook.
- `plugin.subscribe_event(...)` declares an event once. The declaration holds the data model, the
  config of its subscription, and its handlers. The library sends the subscription again after every
  reconnect, so a subscription cannot stay lost
  ([ADR-0017](./docs/adr/0017-declared-events-are-resubscribed.md)).
  - The call hands back a wrapped handler that carries `dispose()`. A caller that awaits the call
    subscribes at once.
  - An event can also be named by its wire name. Then the library decodes nothing, and the handler
    gets the raw payload.
  - A subscription that VTS refuses now reaches the new `on_subscribe_failed` hook. It no longer
    fails the authentication.
- `call_api` and `subscribe_event` are generated into a stub, typed per model. `handle_event` is a
  generic method on `Plugin`.
  - CI fails when the stub and the models disagree.
  - `subscribe_event` gets one typed overload per event. The `config` argument is optional only when
    the event config model has no required field.
- The ArtMesh groups are modelled too: `ArtMeshMatcher.art_mesh_group_id_exact`, plus
  `ArtMeshListResponse.number_of_art_mesh_groups` and `art_mesh_groups`, which carry the new
  `ArtMeshGroup` (`groupID`, `groupName`, `numberOfArtMeshesInGroup`, `artMeshNames`).
- `ExpressionInfo.seconds_since_last_active` reads how long ago an expression was active — a field
  VTube Studio sends that its own documents leave out.

### Changed

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
- `plugin.reconnect()` asks for a fresh session instead of opening one itself. While the plugin runs,
  the call drops the current session and the run opens and authenticates the next one — so a drop
  that is still waiting out `reconnect_delay` retries immediately. `wait_connect=True` waits for the
  new socket, not for authentication. A call while a connect is already in flight does nothing now
  instead of raising `RuntimeError`, and a reconnect by hand no longer ends the run that owns the
  connection ([ADR-0019](./docs/adr/0019-the-run-owns-the-session.md)).
- A field the models do not declare is kept instead of dropped, on frames and on the payloads you
  build alike ([ADR-0020](./docs/adr/0020-unknown-fields-are-kept.md)). The aliases do not rename
  those fields, so write them the way the wire does.

### Removed

- `Plugin.stopped` is gone. The supervisor stops when a caller cancels it, so a caller stops the
  plugin with `await plugin.stop()` and reads the state from `plugin.state`.
- The library does not log. The logging shim, the `log` and `all` extras, and the `cookit`
  dependency are gone ([ADR-0011](./docs/adr/0011-dependency-set.md)).

### Internal

- A pytest suite replays frames that a real VTube Studio captured.
- `CONTEXT.md`, the ADRs, the user guide, and this changelog are new.
- A malformed event frame reaches `on_parse_data_error` once, not once per handler of that event.
- `stop()` disconnects before it sweeps the handler tasks, and a handler re-dispatched after
  `on_handler_run_failed` is tracked like the rest.
- An answer that arrives for a request that already gave up is dropped quietly.

## 0.0.1.alpha2 — 2025-05-21

- This release refactored the project, completed the missing data models, and improved the type
  hints.

## 0.0.1.alpha1 — 2025-04-11

- First alpha release.
