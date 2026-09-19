# 更新日志

[English](CHANGELOG.md) | 简体中文

新版本置顶，日期取 PyPI 上传时间。

## 0.1.0（未发布）

本次发布离开 `0.0` 不稳定线。版本号从此说明一次发布做了什么，包元数据也不再声明 alpha 状态
（ADR-0012）。以下条目都在 `0.0.1.alpha2` 之后落地，且都还没上 PyPI。

- `coovts.types.consts` 现在放着上游常量表：错误码、受限制按键、热键动作，以及后期效果和它们的配置。
- 库补齐了权限流程、之前缺的六个事件、`ItemSort`，以及 api 包与 event 包共用的 ArtMesh 模型。
- 一个基类模型和一个 config 字典取代了每个模型各自的 config 装饰器：`VTSBaseModel` 与
  `vts_base_model_config`（[ADR-0014](./docs/adr/0014-one-model-config-and-a-wire-boundary.md)）。
- 每个 payload 模型现在按字段名和线上别名都能校验。帧和 Python 字典在任何调用点都能解析，代码里也不再
  传 `by_alias=True`（[ADR-0018](./docs/adr/0018-aliases-validate-everywhere.md)）。
- 致命鉴权错误现在直接结束运行。重试修不了的拒绝，库不再重试
  （[ADR-0016](./docs/adr/0016-fatal-authentication-refusals-end-the-run.md)）。
- `stop()` 会取消还在跑的 handler 任务。
- 连接断开时，每个在途请求都以 `NetworkError` 失败。
- 在途请求超过 API 超时后抛 `RequestTimeout`。
- 库完全不打日志。日志 shim、`log` 与 `all` extra，以及 `cookit` 依赖都已删除
  （[ADR-0011](./docs/adr/0011-dependency-set.md)）。
- 库自己发起的断开若关闭失败，失败现在报给新增的 `on_disconnect_failed` hook。
- `Plugin.stopped` 已移除。调用方取消 supervisor 就会让它停下，所以停止插件用 `await plugin.stop()`，
  读状态用 `plugin.state`。
- 生成的 API 类型面现在覆盖 `call_api` 与 `subscribe_event`，按模型给出类型。stub 和模型不一致时 CI
  直接失败。`handle_event` 则是 `Plugin` 上的泛型方法。
- 新增 pytest 套件，回放真实 VTube Studio 抓到的帧。
- 新增 `CONTEXT.md`、ADR、使用指南，以及这份 changelog。
- `plugin.subscribe_event(...)` 一次声明一个事件。声明本身持有数据模型、它订阅用的 config，以及它的
  handler。每次重连后库都会重发订阅，所以订阅不会一直丢着
  （[ADR-0017](./docs/adr/0017-declared-events-are-resubscribed.md)）。
- 这个调用交回一个包过一层的 handler，它带 `dispose()`。await 这个调用则立刻订阅。
- 事件也可以用 wire 名指名。这时库什么都不解析，handler 拿到的是原始 payload。
- VTS 拒绝的订阅现在报给新增的 `on_subscribe_failed` hook，不再让鉴权失败。
- 生成的 stub 为每个事件给 `subscribe_event` 一条带类型的重载。只有对应的 config 模型没有必填字段时，
  `config` 参数才是可选的。

## 0.0.1.alpha2 — 2025-05-21

- 本次发布重构了项目，补齐了缺失的数据模型，也优化了类型提示。

## 0.0.1.alpha1 — 2025-04-11

- 首个 alpha 版本。
