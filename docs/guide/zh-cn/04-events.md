# 事件

> [English](../en/04-events.md)

## 两件独立的事

VTS 的事件要能跑通，**订阅**和 **handler** 缺一不可，而它们是两回事：

- **订阅**：让 VTS 开始推这个事件。这是网络上的动作，会话级。
- **handler**：本地的，VTS 完全不知道它存在。

`plugin.subscribe_event(...)` 一次把两半都声明了，并且由库负责让订阅一直活着：

```python
from coovts.types import event


@plugin.subscribe_event(event.ModelMovedEventData)
async def _(data: event.ModelMovedEventData):
    print(data.model_position)
```

写在模块顶层，只写一次。每次鉴权成功后 VTS 那边都会重新订阅，所以重连不会悄悄让你收不到事件。只想要
handler 的话，就是 `@plugin.handle_event(...)` 注册的东西：它交回来的同样是包过一层的 handler，所以
dispose 它只是停掉分发——它背后没有订阅可以取消。

要点：

- **事件由它的 data 模型来指名**：`XxxEventData` 就是事件 `XxxEvent`，`get_event_config_model(...)` 能找到
  它的 config 模型 `XxxEventConfig`。字段含义看上游：[订阅与取消订阅][e-sub] 与各事件章节。
- **config 是可选的，除非它的模型有必填字段**：默认值就是按 config 模型自己的字段默认值构造出来的，所以
  `subscribe_event(event.ModelOutlineEventData)` 发出去的是 `{"draw": false}`。想自己指定就传一个 config：
  `subscribe_event(event.ModelOutlineEventData, event.ModelOutlineEventConfig(draw=True))`。
  `ArtMeshTrackingEventData`、`ArtMeshOutlineEventData`、`ExpressionToggledEventData` 和
  `TestEventData`（需要 `test_message_for_event`）不能不带 config 声明——它们的 config 有必填字段，而生成
  的 stub 会按事件给 `config` 定类型，所以管着你的是类型检查器。
- **config 不一定是模型**：VTS 在该事件上接受的任何东西（通常是手搓的 dict）都会走不带类型的 overload，原样
  发上去。
- **`await plugin.subscribe_event(...)`** 会立刻把订阅发出去，返回 `EventSubscriptionResponse`，同时照样
  登记这个声明。运行时算出来的 config 就是这么发出去的。
- **`await on_moved.dispose()`** 会放弃这个事件：handler 是被包了一层才交回来的，所以你装饰的那个函数身上
  就带着 `dispose`，它会取消订阅并忘掉这个 registration。还没挂 handler 的声明就用 `subscribe_event` 返回
  的对象同样 dispose。
- **声明被拒绝会走 `on_subscribe_failed`**，带上 registration 和异常，其它都不会丢：会话继续开着，下次鉴权
  会再试一次。而 await 的那次订阅是在 await 处抛 `APIError`。
- **这个包没有建模的模型**走泛用 overload：`plugin.subscribe_event(MyEventData, MyConfig())`，那里 config 是
  `Any`——传错不会被类型层拦住，拦它的是 VTS。
- **事件也可以用 wire 名来指名**：`handle_event("ModelMovedEvent")`，或者
  `subscribe_event("ModelMovedEvent", config)`。这种形式什么都不解析、也不校验：handler 拿到的是原始
  payload，类型是 `Any`；config 不传就发空 config。手搓 `api.EventSubscriptionRequest` 经 `call_api` 发出
  去，仍然是最后的兜底。

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

- 想确认「到底有没有订阅上」：看 `EventSubscriptionResponse.subscribed_event_count`——await 过的声明会返回
  它，除此之外它只会在 `on_subscribe_failed` 里以失败的形式出现。声明过的事件在 `plugin.subscriptions`
  里。
- 想确认「帧到底有没有来」：挂 `on_recv_raw` 看原始 JSON；如果来了但 handler 没触发，那是没订阅或是
  载荷解不成模型（后者会走 `on_parse_data_error`）。
- 先拿 `TestEventData` 试链路：它就是为了端到端测事件 API 存在的。

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
