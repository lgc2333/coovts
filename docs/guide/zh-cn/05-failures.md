# 出错的时候

> [English](../en/05-failures.md)

## 一条分界线：hook 侧 vs `await` 侧

这是整个库最需要先搞明白的一件事：

| 你在哪看到错误               | 看到的是什么                                                                            |
| ---------------------------- | --------------------------------------------------------------------------------------- |
| hook（`on_xxx`）             | 传输层抛出的**原样异常**，也可能是库类型。比如一个 `ConnectionClosed` 还带着 close code |
| `await plugin.call_api(...)` | **只会是库类型**：`APIError` / `ValidationError` / `RequestTimeout` / `NetworkError`    |

于是 `on_authenticate_failed(e)` 里的 `e` 可能是 `APIError`（VTS 明确拒绝），也可能是
`ConnectionClosed`（socket 断了）。**想区分这两种，必须自己 `isinstance(e, APIError)`。**
同理，连接类失败不会变成 `await` 侧的一种异常，因为那时候根本没有请求在等。库自己发起的一次断开失败了
也一样只走 hook：`on_disconnect_failed`，不会出现在 `await` 处。

这也解释了为什么没有 `on_disconnected` 这种回调：断开这件事的可见后果，就是「在途请求全以
`NetworkError` 失败」加上「`on_connection_closed` 收到传输异常」，再加一个专门的 hook 只是多一条
可能被忘记处理的路径。

## 哪些鉴权失败会让插件停下来

有些鉴权失败重试一万次也一样：VTS 已经做出决定了（用户拒绝、请求非法、token 失效）。这类错误会让
supervisor 直接结束运行，状态落到 `STOPPED`：

| 错误码 | 含义             |
| ------ | ---------------- |
| 1      | API 访问被关闭   |
| 2      | JSON 非法        |
| 3      | API 名非法       |
| 4      | API 版本非法     |
| 50     | Token 申请被拒绝 |
| 52     | 插件名非法       |
| 53     | 开发者名非法     |
| 54     | 插件图标非法     |
| 100    | 鉴权 token 缺失  |
| 101    | 插件名缺失       |
| 102    | 开发者名缺失     |

反过来说，这些**不**会让插件停下：51（申请弹窗正开着）和 5（重试会换一个新的 requestID），以及其他
一切可能换个时间就成功的失败。理由见
[ADR-0016](../../adr/0016-fatal-authentication-refusals-end-the-run.md)。

## 什么永远不会被自动重试

- **在途请求**：断线就失败，重连成功也不会替你重发。要不要重来由你决定（[ADR-0008](../../adr/0008-request-correlation-and-error-surface.md)）。
- **事件**：断了就是丢了，VTS 不重放。想让状态收敛，就在 `on_authenticated` 里主动重问一次。
- **连接本身**：会重试，但只是定延重连（[ADR-0007](../../adr/0007-reconnect-is-a-fixed-delay-loop.md)）。

## 还没做的东西

- UDP 服务发现，以及非请求式的 `VTubeStudioAPIStateBroadcast`：端点目前只能手配。这是**还没做**，
  不是不做（[ADR-0004](../../adr/0004-vts-api-coverage.md)），登记在 [backlog](../../backlog.md)。

## 库有意不做的事

有意的排除（[ADR-0013](../../adr/0013-non-goals.md)）：

- 不镜像 VTS 的状态（模型/物品列表、参数值、订阅情况），要就现问。
- 不给 handler 排序和背压。
- 不支持 API 版本协商：只对当前 API 版本，不对旧版 VTS 做降级。
- py3.12 以下不支持，也不提供兼容层。

## 排查顺序

1. `on_connect_failed` / `on_connection_closed` / `on_disconnect_failed`：连接层到底通不通，异常原样
   打出来。
2. `on_recv_raw` / `on_before_send_raw`：线上实际流动的 JSON。
3. `on_parse_data_error`：帧到了但解不出来（信封坏了，或者载荷和模型对不上）。
4. `on_handler_run_failed`：你的业务代码抛了异常。
5. `await` 处的库异常类型：请求级失败的具体原因，`APIError.data.error_id` 查 ErrorID 表。

## 回到开头

[指南首页](./README.md)
