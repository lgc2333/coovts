# 事件

> [English](../en/04-events.md)

## 两件独立的事

VTS 的事件要能跑通，**订阅**和 **handler** 缺一不可，而它们是两回事：

- **订阅**：给 VTS 发 `EventSubscriptionRequest`，让它开始推这个事件。这是网络上的动作，会话级。
- **handler**：在本地用 `@plugin.handle_event(...)` 注册回调。VTS 完全不知道它存在。

两种半成品都是静默失效：只订阅不挂 handler，帧照收、然后被丢掉；只挂 handler 不订阅，永远不触发。

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

要点：

- **事件名从模型类名推导**：`XxxEventData` / `XxxEventConfig` 去掉后缀就是事件名，也可以用
  `get_event_name(...)` 现成地取。data 模型和 config 模型共享同一个事件名。
- **`config` 是必填字段**，即使这个事件没有配置项（那就传 `XxxEventConfig()`）。忘传会在构造时就报错。
  上游事件不同 config 字段的含义见 [订阅与取消订阅][e-sub] 与各事件章节。
- **订阅要放在 `on_authenticated`**，因为它是会话级的：重连之后 VTS 那边什么都不记得了。
- **取消订阅**同样用 `EventSubscriptionRequest`，`subscribe=False`。
- `EventSubscriptionRequest.config` 现在是有意留成 `Any` 的，将来做订阅便捷方法时会按 config 类型推导
  data 类型。

## 分发语义

每个收到的帧，会给每个注册的 handler 各起一个 task，然后就不管了：

- **不保序**：同一个事件的两个 handler 并发跑，慢的那个不会挡住下一帧。
- **无背压**：handler 跟不上事件频率时，任务会堆积而不是让流慢下来。
- **handler 抛异常不会在 `run()` 里冒泡**：异常被捕获后转发给 `on_handler_run_failed`。没注册那个
  hook，异常就此消失。所以线上跑的插件至少要挂一个日志 hook。
- **`stop()` 会取消所有在跑的 handler**：handler 得容忍 `CancelledError`，别吞它。

以上都不是缺口，而是有意为之：handler 就是 fire-and-forget 的。见
[ADR-0006](../../adr/0006-handler-dispatch-is-fire-and-forget.md)。

**没有匹配的帧会被静默丢弃**：未知 messageType、迟到（已被消费过的 requestID）的响应，都是直接扔。
这是有意为之，不是漏了日志。

## 调试

- 想确认「到底有没有订阅上」：看 `EventSubscriptionResponse.subscribed_event_count`。
- 想确认「帧到底有没有来」：挂 `on_recv_raw` 看原始 JSON；如果来了但 handler 没触发，那是没订阅或是
  载荷解不成模型（后者会走 `on_parse_data_error`）。
- 先拿 `TestEventData` 试链路：它就是为了测事件 API 存在的。

## 各个事件的字段含义在哪

| 事件模型                               | 上游章节                                           |
| -------------------------------------- | -------------------------------------------------- |
| `TestEventData`                        | [Test event][e-test]                               |
| `ModelLoadedEventData`                 | [模型加载/卸载][e-model-loaded]                    |
| `TrackingStatusChangedEventData`       | [追踪丢失/恢复][e-tracking]                        |
| `BackgroundChangedEventData`           | [背景改变][e-bg]                                   |
| `ModelConfigChangedEventData`          | [模型配置改变][e-model-config]                     |
| `ModelMovedEventData`                  | [模型移动/缩放/旋转][e-model-moved]                |
| `ModelOutlineEventData`                | [模型轮廓][e-outline]                              |
| `HotkeyTriggeredEventData`             | [热键触发][e-hotkey]                               |
| `ExpressionToggledEventData`           | [表情激活/停用][e-expression]（beta）              |
| `ModelAnimationEventData`              | [动画事件][e-anim]                                 |
| `ItemEventData`                        | [物品事件][e-item]                                 |
| `ModelClickedEventData`                | [模型被点击][e-click]                              |
| `PostProcessingEventData`              | [后期处理事件][e-vfx]                              |
| `Live2DCubismEditorConnectedEventData` | [Cubism Editor 连接][e-cubism]                     |
| `ArtMeshTrackingEventData`             | [跟踪 ArtMesh 上的自定义点][e-track-point]（beta） |
| `ArtMeshOutlineEventData`              | [跟踪 ArtMesh 轮廓][e-artmesh-outline]（beta）     |

带 beta 标记的只存在于 VTS 公测分支。

## 下一步

[出错的时候](./05-failures.md)

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
