# 更新日志

[English](CHANGELOG.md) | 简体中文

新版本在最上面，日期取 PyPI 上传时间。`0.0` 线什么也不承诺，版本号也不代表这次改了多大；从 `0.1` 起
minor 就是放破坏性变更的地方（[ADR-0012](./docs/adr/0012-public-api-and-versioning.md)）。

## 0.1.0（未发布）

离开 `0.0` 不稳定线：版本号从此代表发布内容，包元数据也不再声明 alpha 状态（ADR-0012）。以下内容都在
`0.0.1.alpha2` 之后落地，目前还没上 PyPI。

- 把上游的常量表逐条转写进 `coovts.types.consts`：错误码、热键动作、后期效果及其配置、受限制的按键。
- 补上权限流程、之前缺的六个事件、`ItemSort`，以及 api 与 event 两包共用的 ArtMesh 模型。
- 用统一的 `VTSBaseModel` / `vts_base_model_config` 取代每个模型各自的 config 装饰器。
- payload 模型现在按字段名和线上别名都能校验：帧和 Python 字典在任何调用点都能解析，`by_alias=True`
  不再需要（[ADR-0018](./docs/adr/0018-aliases-validate-everywhere.md)）。
- 重试也修不了的鉴权拒绝现在直接结束运行，不再空转；`stop()` 会取消还在跑的 handler 任务。
- 连接断开时在途请求以 `NetworkError` 失败，超过 deadline 的请求抛 `RequestTimeout`。
- 删掉日志 shim、`log` / `all` extra 与 `cookit` 依赖：库完全不打日志
  （[ADR-0011](./docs/adr/0011-dependency-set.md)）。
- 新增 `on_disconnect_failed` hook：库自己发起的断开若关闭失败，就报到这里。
- `Plugin.stopped` 已移除：supervisor 靠取消来停止，所以停止用 `await plugin.stop()`，状态读
  `plugin.state`。
- `call_api` 与 `subscribe_event` 由模型生成到 stub，并加了 CI 检查漂移；`handle_event` 则是 `Plugin`
  上的泛型方法。
- 加了 pytest 套件，用真实 VTube Studio 的抓包帧回放。
- 加了 `CONTEXT.md`、ADR、使用指南，以及这份 changelog。
- 事件现在用 `plugin.subscribe_event(...)` 声明一次：handler 与订阅绑在一起，每次重连后自动重发；交回来的
  handler 被包了一层、带 `dispose()`，而 await 声明本身则立刻订阅。事件也可以用 wire 名指名，这时什么都不
  解析，handler 拿到的是原始 payload。
- VTS 拒绝的订阅不再让鉴权失败，改报到新增的 `on_subscribe_failed` hook。
- 生成的 stub 为每个事件多了一条带类型的 `subscribe_event` 重载，其 `config` 只有在对应 config
  模型没有必填字段时才是可选的。

## 0.0.1.alpha2 — 2025-05-21

- 重构项目，补齐缺失的数据模型，类型提示做得更好。

## 0.0.1.alpha1 — 2025-04-11

- 首个 alpha 版本。
