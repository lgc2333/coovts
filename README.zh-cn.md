<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

<a href="https://github.com/lgc2333/coovts">
  <img src="https://raw.githubusercontent.com/lgc2333/coovts/main/assets/coovts.svg" width="315" alt="CooVTS Logo">
</a>

# CooVTS

_✨ 另一个写 VTube Studio 插件的 Python 库 ✨_

[English](README.md) | 简体中文

[![CI](https://github.com/lgc2333/coovts/actions/workflows/ci.yml/badge.svg)](https://github.com/lgc2333/coovts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/lgc2333/coovts/branch/main/graph/badge.svg)](https://codecov.io/gh/lgc2333/coovts)
[![PyPI](https://img.shields.io/pypi/v/coovts)](https://pypi.org/project/coovts/)
[![Python versions](https://img.shields.io/pypi/pyversions/coovts)](https://pypi.org/project/coovts/)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

</div>

## ✨ 特性

- ✨ 完整的类型提示，支持静态类型检查
- 🎯 用 Pydantic 做数据校验与序列化
- 🔄 异步优先，基于 WebSocket 通信
- 🎨 好用的插件事件系统
- 🛡️ 内置错误处理与重连机制

## 📖 简介

### 风格速览

```python
import asyncio

from coovts.plugin import Plugin
from coovts.types import api, event, get_event_name

# no token yet: VTS asks the user once
plugin = Plugin("A Creative Plugin Name", "LgCuwukii☆")


@plugin.on_authenticated
async def _():  # runs once per session, reconnects included
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


asyncio.run(plugin.run())
```

### 接下来

- 看看详细的[使用指南](./docs/guide/zh-cn/README.md)
- 看看 [`examples/basic.py`](./examples/basic.py) ——同一个插件，但把每个日志 hook 都填满了。

感谢各位使用，也欢迎大家贡献 😊

## 💿 安装

需要 Python 3.12 及以上。

```bash
pip install coovts
```

_or_

```bash
uv add coovts
```

没有 extra，也没有日志依赖：运行时就是 Pydantic + `websockets`，而插件需要知道的一切都通过 hook 或
异常交给你（[ADR-0011](./docs/adr/0011-dependency-set.md)）。

## 📞 联系方式

- Telegram：[@lgc2333](https://t.me/lgc2333)
- QQ：3076823485 / 群：[168603371](https://qm.qq.com/q/EikuZ5sP4G)
- 邮箱：[lgc2333@126.com](mailto:lgc2333@126.com)
- Discord：[lgc2333](https://discordapp.com/users/810486152401256448)（不常看）

## 📝 更新日志

[CHANGELOG.zh-cn.md](./CHANGELOG.zh-cn.md)
