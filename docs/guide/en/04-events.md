# Events

> [简体中文](../zh-cn/04-events.md)

## Two separate things

For a VTS event to reach your code you need **a subscription** and **a handler**, and they are not
the same thing:

- **The subscription** is what makes VTS push the event. It is a network action, and it is
  session-scoped.
- **The handler** is local. VTS knows nothing about it.

`plugin.subscribe_event(...)` declares both halves at once, and the library keeps the subscription
alive:

```python
from coovts.types import event


@plugin.subscribe_event(event.ModelMovedEventData)
async def _(data: event.ModelMovedEventData):
    print(data.model_position)
```

Write it at module level, once. VTS is subscribed to right after every successful authentication, so
a reconnect cannot silently leave you without events. A handler on its own is what
`@plugin.handle_event(...)` registers: it hands back the same wrapped handler, so disposing of it
only stops the dispatch — there is no subscription behind it to cancel.

The details that matter:

- **The event is named by its data model.** `XxxEventData` is the event `XxxEvent`, and
  `get_event_config_model(...)` finds its config model, `XxxEventConfig`. Field meaning is upstream:
  [Subscribing and unsubscribing][e-sub] and the section per event.
- **A config is optional, unless its model has a required field.** The default is the config model
  built from its own field defaults, so `subscribe_event(event.ModelOutlineEventData)` sends
  `{"draw": false}`. Pass a config to choose: `subscribe_event(event.ModelOutlineEventData,
event.ModelOutlineEventConfig(draw=True))`. `ArtMeshTrackingEventData`,
  `ArtMeshOutlineEventData`, `ExpressionToggledEventData` and `TestEventData` (which needs
  `test_message_for_event`) cannot be declared without one — their configs have required fields, and
  the generated stub types `config` per event, so the type checker is what holds you to it.
- **A config does not have to be a model**: anything VTS accepts for that event — a hand-built dict,
  typically — goes through the untyped overload and out untouched.
- **`await plugin.subscribe_event(...)`** sends the subscription right away, returns the
  `EventSubscriptionResponse`, and registers the declaration all the same. That is how a config
  computed at runtime gets sent.
- **`await on_moved.dispose()`** gives the event up: the handler comes back wrapped, so the function
  you decorated carries `dispose`, which cancels the subscription and forgets the registration. A
  declaration that has no handler yet is disposed of the same way, off the object `subscribe_event`
  returned.
- **A refused declaration reaches `on_subscribe_failed`** with the registration and the error, and
  nothing else is lost: the session stays up and the next authentication tries again. A subscription
  you `await`ed instead raises the `APIError` at the await.
- **A model this package does not model** goes through the generic overload:
  `plugin.subscribe_event(MyEventData, MyConfig())`, whose config is `Any` — a wrong one is not caught
  there, and VTS is the one that refuses it.
- **An event can also be named by its wire name**: `handle_event("ModelMovedEvent")`, or
  `subscribe_event("ModelMovedEvent", config)`. Nothing is decoded or validated, the handler gets the
  raw payload typed `Any`, and an omitted config goes out empty. Hand-built
  `api.EventSubscriptionRequest` frames through `call_api` stay the last resort.

## Dispatch semantics

For every frame that arrives, each registered handler gets its own task, and then nothing waits for
it:

- **No ordering**: two handlers for the same event run concurrently, and a slow one does not hold up
  the next frame.
- **No backpressure**: a handler that lags behind the event rate accumulates tasks instead of slowing
  the stream down.
- **A handler's exception does not surface in `run()`**: it is caught and re-dispatched to
  `on_handler_run_failed`. With no such hook registered, the exception disappears. Any plugin running
  for real should at least have a logging hook.
- **`stop()` cancels every running handler**, so handlers must tolerate `CancelledError` rather than
  swallow it.

None of that is an oversight: handlers are fire-and-forget by design. See
[ADR-0006](../../adr/0006-handler-dispatch-is-fire-and-forget.md).

**A frame with nothing to match is dropped silently**: an unknown messageType, or a late response
whose `requestID` was already consumed. That is intended, not a missing log line.

## Debugging

- To check whether a subscription went through, look at
  `EventSubscriptionResponse.subscribed_event_count` — returned by an awaited declaration, and
  otherwise visible only as a failure on `on_subscribe_failed`. Declared events are in
  `plugin.subscriptions`.
- To check whether frames actually arrive, add `on_recv_raw` and look at the raw JSON. If a frame
  arrives but your handler does not run, either you never subscribed or the payload failed to decode
  (that one goes to `on_parse_data_error`).
- `TestEventData` exists to exercise the event API end to end — the cheapest link test there is.

## Where the per-event field docs live

| Event model                            | Upstream section                                              |
| -------------------------------------- | ------------------------------------------------------------- |
| `TestEventData`                        | [Test event][e-test]                                          |
| `ModelLoadedEventData`                 | [Model loaded/unloaded][e-model-loaded]                       |
| `TrackingStatusChangedEventData`       | [Lost/found tracking][e-tracking]                             |
| `BackgroundChangedEventData`           | [Background changed][e-bg]                                    |
| `ModelConfigChangedEventData`          | [Model config modified][e-model-config]                       |
| `ModelMovedEventData`                  | [Model moved/resized/rotated][e-model-moved]                  |
| `ModelOutlineEventData`                | [Model outline changed][e-outline]                            |
| `HotkeyTriggeredEventData`             | [Hotkey triggered][e-hotkey]                                  |
| `ExpressionToggledEventData`           | [Expression activated/deactivated][e-expression] (beta)       |
| `ModelAnimationEventData`              | [Animation event triggered][e-anim]                           |
| `ItemEventData`                        | [Item event][e-item]                                          |
| `ModelClickedEventData`                | [Model clicked][e-click]                                      |
| `PostProcessingEventData`              | [Post-processing event][e-vfx]                                |
| `Live2DCubismEditorConnectedEventData` | [Cubism Editor connected][e-cubism]                           |
| `ArtMeshTrackingEventData`             | [Tracking a custom point on an ArtMesh][e-track-point] (beta) |
| `ArtMeshOutlineEventData`              | [Tracking an ArtMesh outline][e-artmesh-outline] (beta)       |

The beta ones exist only on VTube Studio's public beta branch.

## Next

[When things fail](./05-failures.md)

[e-sub]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#subscribing-and-unsubscribing
[e-test]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#test-event
[e-model-loaded]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#model-loadedunloaded
[e-tracking]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#lostfound-tracking
[e-bg]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#background-changed
[e-model-config]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#model-config-modified
[e-model-moved]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#model-movedresizedrotated
[e-outline]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#model-outline-changed
[e-hotkey]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#hotkey-triggered
[e-expression]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#expression-activateddeactivated-event
[e-anim]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#animation-event-triggered
[e-item]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#item-event
[e-click]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#model-clicked-event
[e-vfx]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#post-processing-event
[e-cubism]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#live2d-cubism-editor-connected-event
[e-track-point]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#track-custom-point-on-artmesh-event
[e-artmesh-outline]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md#track-artmesh-outline-event
