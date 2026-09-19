# 更新日志

[English](CHANGELOG.md) | 简体中文

最新版本在最上面，日期取 PyPI 上传时间。

## 0.1.0 — 2026-09-20

### 新增

- `coovts.types.consts` 现在放着上游常量表：错误码、受限制按键、热键动作，以及后期效果和它们的配置。
- 库补齐了权限流程、此前缺的事件、`ItemSort`，以及 api 包与 event 包共用的 ArtMesh 模型。
- 库自己发起的断开若关闭失败，失败现在报给新增的 `on_disconnect_failed` hook。
- `plugin.subscribe_event(...)` 一次声明一个事件。声明本身持有数据模型、它订阅用的 config，以及它的
  handler。每次重连后库都会重发订阅，所以订阅不会一直丢着
  （[ADR-0017](./docs/adr/0017-declared-events-are-resubscribed.md)）。
  - 这个调用交回一个包过一层的 handler，它带 `dispose()`。await 这个调用则立刻订阅。
  - 事件也可以用 wire 名指名。这时库什么都不解析，handler 拿到的是原始 payload。
  - VTS 拒绝的订阅现在报给新增的 `on_subscribe_failed` hook，不再让鉴权失败。
- `call_api` 与 `subscribe_event` 由模型生成到 stub，按模型给出类型；`handle_event` 则是 `Plugin`
  上的泛型方法。
  - stub 和模型不一致时 CI 直接失败。
  - `subscribe_event` 为每个事件给出一条带类型的重载。只有对应的 config 模型没有必填字段时，`config`
    参数才是可选的。
- ArtMesh 群组也建进模型了：`ArtMeshMatcher.art_mesh_group_id_exact`，以及
  `ArtMeshListResponse.number_of_art_mesh_groups` 与 `art_mesh_groups`，它们装着新的 `ArtMeshGroup`
  （`groupID`、`groupName`、`numberOfArtMeshesInGroup`、`artMeshNames`）。
- `ExpressionInfo.seconds_since_last_active` 读得到表情上次激活过去了多久——VTS 会发这个字段，但它自己
  的文档里没有。

### 变更

- 一个基类模型和一个 config 字典取代了每个模型各自的 config 装饰器：`VTSBaseModel` 与
  `vts_base_model_config`（[ADR-0014](./docs/adr/0014-one-model-config-and-a-wire-boundary.md)）。
  - 每个 payload 模型现在按字段名和线上别名都能校验。帧和 Python 字典在任何调用点都能解析，代码里也不
    再传 `by_alias=True`（[ADR-0018](./docs/adr/0018-aliases-validate-everywhere.md)）。
- 致命鉴权错误现在直接结束运行。重试修不了的拒绝，库不再重试
  （[ADR-0016](./docs/adr/0016-fatal-authentication-refusals-end-the-run.md)）。
- `stop()` 会取消还在跑的 handler 任务。
- 连接断开时，每个在途请求都以 `NetworkError` 失败。
- 在途请求超过 API 超时后抛 `RequestTimeout`。
- `plugin.reconnect()` 变成「请求一个新会话」，不再自己开一个。插件在跑的时候，这个调用断开当前会话，由
  跑着的那条运行开下一个并鉴权——所以正等着 `reconnect_delay` 的掉线会立刻重试。`wait_connect=True` 只等到
  新 socket 建好，不等鉴权；没有 run 时，如果它加入的是一次已经在建的连接，拿到的是那次连接失败的原因，而不是
  去等一个不会到来的成功（有 run 时它照样只等 socket，连接失败由 run 重试）。连接已经在建时再调，现在什么都
  不做，不再抛 `RuntimeError`；手动重连也不会再把持有连接的运行打死
  （[ADR-0019](./docs/adr/0019-the-run-owns-the-session.md)、
  [ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)）。
- `stop()` 之后 `reconnect()` 就是终局：在 `run()` 重新启动插件之前，这个调用抛 `RuntimeError`；因为「重试
  也修不了的鉴权拒绝」而结束的 run 也一样（[ADR-0016](./docs/adr/0016-fatal-authentication-refusals-end-the-run.md)）。
  `stop()` 也会取消还在建立中的连接，而不是把它本来会接手的 socket 留在身后
  （[ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)）。
- `stop()` 只忘掉它自己结束的那条运行，所以 stop 收尾期间启动的运行之后仍然停得掉。
- 鉴权途中掉线的会话现在会等满 `reconnect_delay`，和其它失败尝试一样，不再按事件循环速度狂重连——接收循环
  自己的等待正好会被下一个会话取消，延迟就是在这条路径上丢掉的。
- `AuthenticationTokenRequest` 不再被 `api_timeout` 切断。它的答案是用户在 VTube Studio 弹窗上点一下，所以
  它会一直等下去，而不是把会话丢掉再问一次、让第一个弹窗还挂在屏幕上
  （[ADR-0016](./docs/adr/0016-fatal-authentication-refusals-end-the-run.md)）。
- 放弃 `reconnect()` 的调用方不再把插件持有的连接一起取消，所以那次连接的其它等待者照样能拿到 socket 或它的
  失败原因（[ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)）。
- 会话开头那次 teardown 里失败的 close 会报给 `on_disconnect_failed`，不再被当成 `on_connect_failed`。
- 不带 config 再声明一次同一个事件，不再覆盖先前那次声明选定的 config——包括 config 模型有必填字段的那几个
  事件，它们以前会在第二次声明时直接抛错
  （[ADR-0022](./docs/adr/0022-one-registration-per-event-name.md)）。
- `ItemPinRequest.pin_info` 变成可选，所以上游文档写明的 unpin payload（`pin=false`，不需要其它信息）现在
  构造得出来、也发得出去。
- `TestEventConfig.test_message_for_event` 默认 `""`，也就是上游说的那个可选字段，所以
  `subscribe_event(event.TestEventData)` 不再需要显式传 config。
- `on_authenticated` 只为还活着的会话触发。声明过的事件正在重新订阅时掉线，会直接重连，而不是让每次会话的
  初始化跑去面对一个已经没了的 socket。
- 先用 wire 名、再用数据模型声明同一个事件，现在会补全那一份注册：handler 按模型解析，订阅带的是该模型默认
  值描述出来的 config。两个不同模型指同一个事件会抛 `ValueError`
  （[ADR-0022](./docs/adr/0022-one-registration-per-event-name.md)）。
- 模型没声明的字段现在会保留，不再丢弃：帧上和你自己构建的 payload 上都一样
  （[ADR-0020](./docs/adr/0020-unknown-fields-are-kept.md)）。别名不改写这些字段，所以要按 wire 的写法
  写它们。
- `stop()` 允许在 hook 或 handler 里调用。发起这次调用的那个会被排除在清扫之外，因为取消它就等于取消那个
  又要取消它自己的 gather；在此之前，这个调用永不返回，进程最终以栈溢出结束
  （[ADR-0021](./docs/adr/0021-a-connect-has-an-owner.md)）。
- `ItemSortRequest.set_split_point` 与 `set_back_order` 变成可选。VTS 对非 Live2D 物品完全忽略这两个字段，
  上游也说留空或写 `null` 即可，所以现在不带它们也能构造出那个 payload。
- `EventSubscriptionRequest.event_name` 与 `config` 接受 `None`。两者依然是必填的，所以每个字段都是显式传
  的：`EventSubscriptionRequest(event_name=None, config=None, subscribe=False)` 就是上游写明的「一次退订
  全部事件」。
- `ExpressionToggledEventConfig` 的两个字段都给了 `False` 默认值，于是这个原本没有可选 config 字段的 beta
  事件，也能像其它事件一样订阅。
- 序列化不了的 payload 不再留下在途请求：序列化挪进了那个「无论怎么退出都会忘掉这个请求」的块里。异常本身不变。
- 省略 `response_model` 时，生成的 API 表面现在标成 `BaseModel`。应答依然由 payload 推导——它的 `resp_m` /
  `resp_t`，否则按命名约定——所以那是个模型；只有显式传 `response_model=None` 才拿原始 body。以前两种写法都
  被标成 `dict[str, Any]`。
- 有三个请求的答案是人在操作，而不是 VTS：带自定义数据的 `ItemLoadRequest`、传了 `requested_permission` 的
  `PermissionRequest`，以及 `ArtMeshSelectionRequest`。API 超时照样会在弹窗还开着的时候把它们切断，所以这三
  个请传 `api_timeout=None`。
- 载荷里的非有限浮点数会以 JSON `null` 发出去。`nan` 与 `inf` 到了 VTS 就是 `null`，而且不会报错，所以请在
  发送前自己拒绝或夹取。

### 移除

- `Plugin.stopped` 已移除。调用方取消 supervisor 就会让它停下，所以停止插件用
  `await plugin.stop()`，读状态用 `plugin.state`。
- 库完全不打日志。日志 shim、`log` 与 `all` extra，以及 `cookit` 依赖都已删除
  （[ADR-0011](./docs/adr/0011-dependency-set.md)）。

### 内部

- 新增 pytest 套件，回放真实 VTube Studio 抓到的帧。
- 新增 `CONTEXT.md`、ADR、使用指南，以及这份 changelog。
- 一帧事件解析失败只会报给 `on_parse_data_error` 一次，不再按该事件挂了多少 handler 重复上报。
- `stop()` 先断连再清扫 handler 任务；`on_handler_run_failed` 之后重派发的 handler 也会被一起跟踪。
- 请求已经放弃之后才到的应答会被安静丢掉。
- 请求在 `send` 还没结束时就失败，不再留下一个等着 asyncio 打日志的异常——不打日志的库（ADR-0011）还是不
  打日志。
- `HotkeyAction.Unset` 不再声称没有 payload 用它：上游自己的 `hotkeyList` 示例就发 `"type": "Unset"`，
  `docs/adr/0015` 里那句也一并改正了。
- 指南的逃生舱示例给出了 `msg_t` 与 `resp_m` 的可用写法：两者都必须是 `ClassVar`，裸写
  `resp_m = SomeModel` 不是 pydantic 认得的字段。
- ADR-0021 记下了「`stop()` 可以在 hook 或 handler 里调用」，以及为什么发起调用的那个会被排除在清扫之外。

## 0.0.1.alpha2 — 2025-05-21

- 本次发布重构了项目，补齐了缺失的数据模型，也改好了类型提示。

## 0.0.1.alpha1 — 2025-04-11

- 首个 alpha 版本。
