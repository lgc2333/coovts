# 快速上手

> [English](../en/01-getting-started.md)

## 环境

需要 Python >= 3.12。`pip install coovts` 即可。

库自身不带任何日志：没有日志依赖，也没有一行日志。所有值得知道的事都通过 hook 或异常交给你
（[ADR-0011](../../adr/0011-dependency-set.md)）。

## 最小插件

```python
import asyncio
import sys
from pathlib import Path

from coovts.plugin import Plugin
from coovts.types import api, event

AUTH_TOKEN_FILE = Path(__file__).parent / "auth_token.txt"

plugin = Plugin(
    "My Plugin",
    "My Name",
    Path(__file__).parent / "icon.png",
    authentication_token=(
        AUTH_TOKEN_FILE.read_text().strip() if AUTH_TOKEN_FILE.exists() else None
    ),
)


@plugin.on_authentication_token_got
async def _(token: str):
    AUTH_TOKEN_FILE.write_text(token)


@plugin.on_authenticate_failed
async def _(e: Exception):
    AUTH_TOKEN_FILE.unlink(missing_ok=True)


@plugin.subscribe_event(event.ModelMovedEventData)
async def _(data: event.ModelMovedEventData):
    print("model moved:", data.model_position)


@plugin.on_authenticated
async def _():
    model = await plugin.call_api(api.CurrentModelRequest())
    print("current model:", model.model_name, model.model_id)


async def main() -> int:
    await plugin.run()
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
```

带全部日志 hook 的完整版见 [`examples/basic.py`](../../../examples/basic.py)。

请求需要有会话，所以 `call_api` 同样写在 `on_authenticated` 里；它按请求给出类型，返回对应的响应模型
（见[发请求](./03-requests.md)）。

## 三件容易踩的事

### 1. 每会话初始化要放在 `on_authenticated` 里

`on_authenticated` **每个会话都触发一次**，重连之后也触发。事件订阅同样是会话级的，但这一半由库负责：
声明过的事件会在 hook 触发前重新订阅一次，所以不会被重连忘掉。其余 VTS 会忘掉的东西——自定义参数、
创建出来的 id、缓存的列表——就得你自己来：放进 `on_authenticated`，而不是 `main()`。理由见
[ADR-0007](../../adr/0007-reconnect-is-a-fixed-delay-loop.md)。

### 2. token 是库交给你保管的

- 构造 `Plugin` 时不传 `authentication_token`，库会先发 `AuthenticationTokenRequest`（带上
  `plugin_name` / `plugin_developer` / `plugin_icon`），拿到 token 后触发
  `on_authentication_token_got`，**由你自己持久化**。
- 传了 token 就直接鉴权，不会再申请一次。
- VTS 判定鉴权失败时，库会抛 `AuthenticationFailedError` **并把 `plugin.authentication_token` 清空**，
  所以下一轮重试不会拿着同一个废 token 再撞一次。这也是为什么在 `on_authenticate_failed` 里删掉自己
  存的 token 是推荐做法。
- `plugin_icon` 接受 `str`（已经是 base64）、`bytes` 或 `Path`，后两种由库负责编码。
- 鉴权流程本身（弹窗、token 含义）看上游 → [Authentication][s-auth]。名字长度等硬性要求同样在上游。

### 3. VTS 没开不会让你的程序崩

`await plugin.run()` 不会因为连不上而抛异常：连接失败走 `on_connect_failed`，等 `reconnect_delay`
（默认 5 秒）后重试，如此循环。先开插件再开 VTS、或者中途关掉 VTS 再打开，都是预期用法。

想退出就用 `await plugin.stop()`，不要只是取消 `run()` 返回的那个 task。

## 在异步程序里跑阻塞代码

`run_sync` 把同步函数包成协程函数，内部丢进 executor：

```python
from coovts.utils import run_sync

load_token = run_sync(AUTH_TOKEN_FILE.read_text)
token = await load_token()
```

## 下一步

- [连接与生命周期](./02-lifecycle.md)：hook 的完整清单和触发时机。
- [发请求](./03-requests.md)：超时、异常、字段命名。

[s-auth]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#authentication
