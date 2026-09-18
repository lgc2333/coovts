# Events

> [简体中文](../zh-cn/04-events.md)

## Two separate things

For a VTS event to reach your code you need **a subscription** and **a handler**, and they are not
the same thing:

- **The subscription** is what makes VTS push the event. It is a network action, and it is
  session-scoped.
- **The handler** is a local callback registered with `@plugin.handle_event(...)`. VTS knows nothing
  about it.

Either half alone fails silently: a subscription with no handler means frames arrive and are
dropped; a handler with no subscription never fires.

```python
from coovts.types import api, event, get_event_name


@plugin.on_authenticated
async def _():
    await plugin.call_api(
        api.EventSubscriptionRequest(
            event_name=get_event_name(event.ModelMovedEventData),
            subscribe=True,
            config=event.ModelMovedEventConfig(),
        ),
    )


@plugin.handle_event(event.ModelMovedEventData)
async def _(data: event.ModelMovedEventData):
    print(data.model_position)
```

The details that matter:

- **The event name is derived from the model class name**: `XxxEventData` and `XxxEventConfig` minus
  the suffix, or call `get_event_name(...)`. The data model and the config model share one event name.
- **`config` is a required field**, even for events with no configuration (pass `XxxEventConfig()`).
  Omitting it fails at construction time. What the config fields on each event mean is upstream:
  [Subscribing and unsubscribing][e-sub] and the section per event.
- **Subscribe inside `on_authenticated`**, because a subscription is session-scoped: after a
  reconnect VTS remembers nothing.
- **Unsubscribing** is the same request with `subscribe=False`.
- `EventSubscriptionRequest.config` is deliberately left as `Any` for now; the plan for a
  subscribe helper is to derive the data type from the config type.

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
  `EventSubscriptionResponse.subscribed_event_count`.
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
