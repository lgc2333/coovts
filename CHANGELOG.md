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
  new socket, not for authentication, and a `wait_connect` call that joins a connect already in
  flight **without a run** gets that connect's failure instead of waiting for a success that is not
  coming; with a run in progress it still waits for the socket, because the run retries a failed
  connect. A call while
  a connect is already in flight does nothing now instead of raising `RuntimeError`, and a reconnect
  by hand no longer ends the run that owns the connection
  ([ADR-0019](./docs/adr/0019-the-run-owns-the-session.md),
  [ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)).
- `stop()` is final for `reconnect()`: until `run()` starts the plugin again, the call raises
  `RuntimeError`, and so does a run that ended on a fatal authentication refusal
  ([ADR-0016](./docs/adr/0016-fatal-authentication-refusals-end-the-run.md)). A stop also cancels a
  connect that is still opening rather than leaving the socket
  it would have adopted behind it
  ([ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)).
- `stop()` forgets only the run it ended, so a `run()` started while a stop is unwinding can still be
  stopped.
- A drop that lands while the run is authenticating now waits out `reconnect_delay` like every other
  failed attempt, instead of reconnecting at loop speed. The delay was lost on the one path where the
  receive loop's own wait is cancelled by the next session.
- The `AuthenticationTokenRequest` is no longer cut short by `api_timeout`. Its answer is a person
  clicking a popup in VTube Studio, so it waits indefinitely rather than dropping the session and
  asking again while the first popup is still on screen
  ([ADR-0016](./docs/adr/0016-fatal-authentication-refusals-end-the-run.md)).
- A caller that gives up on `reconnect()` no longer cancels the connect the plugin owns, so every
  other caller of that connect still gets its socket or its failure
  ([ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)).
- A close that fails during the leading teardown of a session reaches `on_disconnect_failed` instead
  of being reported to `on_connect_failed`.
- Declaring an event again without a config no longer replaces the config an earlier declaration
  chose — including the events whose config model has a required field, which used to raise on the
  second declaration ([ADR-0022](./docs/adr/0022-one-registration-per-event-name.md)).
- `ItemPinRequest.pin_info` is optional, so the unpin payload upstream documents (`pin=false`, no
  other info) can be built and sent.
- `TestEventConfig.test_message_for_event` defaults to `""`, the optional field upstream describes, so
  `subscribe_event(event.TestEventData)` no longer needs an explicit config.
- `on_authenticated` fires only for a session that is still live. A drop that lands while the declared
  events are being re-subscribed reconnects, instead of running per-session setup against a socket
  that is already gone.
- Declaring an event by its wire name and then by its data model now completes the one registration
  for that event, so its handlers decode with the model and its subscription carries the config that
  model's defaults describe. Two different models naming one event raise `ValueError`
  ([ADR-0022](./docs/adr/0022-one-registration-per-event-name.md)).
- A field the models do not declare is kept instead of dropped, on frames and on the payloads you
  build alike ([ADR-0020](./docs/adr/0020-unknown-fields-are-kept.md)). The aliases do not rename
  those fields, so write them the way the wire does.
- `stop()` can be called from inside a hook or a handler. The one that makes the call is left out of
  the sweep, because cancelling it would cancel the gather that cancels it; before, the call never
  returned and the process ended in a stack overflow
  ([ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)).
- `ItemSortRequest.set_split_point` and `set_back_order` are optional. VTube Studio ignores both for a
  non-Live2D item — upstream says to leave them empty or `null` — so that payload now builds without
  them.
- `EventSubscriptionRequest.event_name` and `config` accept `None`. Both stay required, so every field
  is passed on purpose: `EventSubscriptionRequest(event_name=None, config=None, subscribe=False)` is
  the unsubscribe from every event at once that upstream documents.
- `ExpressionToggledEventConfig` gives both of its fields a default of `False`, so the one beta event
  that had no optional config field can be subscribed to the way its siblings already could.
- A payload that cannot be serialised no longer leaves a pending request behind: the serialisation
  runs inside the block that forgets the request on every exit. The error itself is unchanged.
- An omitted `response_model` is typed as `BaseModel` in the generated API surface. The answer is
  still derived from the payload — its `resp_m` / `resp_t`, else the naming convention — so it is a
  model; only an explicit `response_model=None` returns the raw body. The typing promised
  `dict[str, Any]` for both.
- Three requests are answered by a person rather than by VTube Studio: `ItemLoadRequest` that carries
  custom data, `PermissionRequest` with a `requested_permission`, and `ArtMeshSelectionRequest`. An
  API timeout still cuts such a request off while its popup is on screen, so pass `api_timeout=None`
  for those three.
- A non-finite float in a payload leaves as JSON `null`. `nan` and `inf` reach VTube Studio as `null`
  and nothing raises, so reject or clamp them before you send.

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
- A request that fails while its `send` is still going out no longer leaves an exception for asyncio
  to log, so a library that does not log (ADR-0011) still does not.
- `HotkeyAction.Unset` no longer claims that no payload carries it: upstream's own `hotkeyList`
  example sends `"type": "Unset"`, and `docs/adr/0015` was corrected with it.
- The guide's escape-hatch example shows the working spelling of `msg_t` and `resp_m`: both are
  `ClassVar`s, and a bare `resp_m = SomeModel` is not a field pydantic knows.
- ADR-0021 records that `stop()` is safe to call from a hook or a handler, and why that one is left
  out of the sweep.

## 0.0.1.alpha2 — 2025-05-21

- This release refactored the project, completed the missing data models, and improved the type
  hints.

## 0.0.1.alpha1 — 2025-04-11

- First alpha release.
