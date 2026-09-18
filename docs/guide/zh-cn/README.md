# coovts 使用指南

> [English](../en/README.md)

coovts 是 VTube Studio 插件 API 的异步 Python 客户端。一个 `Plugin` 对象独占一条 WebSocket 连接，
负责鉴权握手、请求与响应的配对、以及把 VTS 推来的事件分发给你的代码。

## 心智模型

- **一个 `Plugin` = 一条连接。** 连接的生命周期（连接 → 鉴权 → 收包 → 断开 → 重连）由库自己的
  supervisor 任务在跑，你的代码通过 **hook** 观察它，而不是自己管 socket。
- **进出 VTS 只有两条路：** 请求（`call_api` / `send_request`）和事件（订阅 + handler）。
- **库不镜像 VTS 的状态。** 模型列表、参数值、订阅情况都按需现问；连接状态机是库唯一的本地状态。

## 读法

| 顺序 | 文档                                | 什么时候看                                    |
| ---- | ----------------------------------- | --------------------------------------------- |
| 1    | [快速上手](./01-getting-started.md) | 第一次跑起来、token 存哪                      |
| 2    | [连接与生命周期](./02-lifecycle.md) | hook 什么时候触发、重连语义、每会话初始化放哪 |
| 3    | [发请求](./03-requests.md)          | 超时、异常、字段命名、未建模的端点            |
| 4    | [事件](./04-events.md)              | 订阅和 handler 的关系、分发语义               |
| 5    | [出错的时候](./05-failures.md)      | 哪一层抛异常、什么会被重试、哪些失败值得重试  |

## 三条约定

1. **术语以 [`CONTEXT.md`](../../../CONTEXT.md) 为准。** 本文使用的 Plugin、Hook、Handler、订阅、
   挂起请求等词，定义都在那里。
2. **本文只写「读代码看不出来」的东西。** 每个请求、每个事件的字段语义都在
   [上游请求文档][req] / [上游事件文档][evt] 里；本文不重复，只在需要时给要点和锚点。
3. **决策的理由在 [`docs/adr/`](../../adr/)。** 本文只说「现在是什么行为」，需要「为什么」时直接链到
   对应的 ADR。

上游链接锚定在 [`docs/references.md`](../../references.md) 记录的同步 commit 上，不随上游改动失效。

[req]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md
[evt]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md
