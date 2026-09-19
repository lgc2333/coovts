<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

<a href="https://github.com/lgc2333/coovts">
  <img src="https://raw.githubusercontent.com/lgc2333/coovts/main/assets/coovts.svg" width="315" alt="CooVTS Logo">
</a>

# CooVTS

_✨ Another library for making VTube Studio plugins with Python ✨_

English | [简体中文](https://github.com/lgc2333/coovts/blob/main/README.zh-cn.md)

[![CI](https://github.com/lgc2333/coovts/actions/workflows/ci.yml/badge.svg)](https://github.com/lgc2333/coovts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/lgc2333/coovts/branch/main/graph/badge.svg)](https://codecov.io/gh/lgc2333/coovts)
[![PyPI](https://img.shields.io/pypi/v/coovts)](https://pypi.org/project/coovts/)
[![Python versions](https://img.shields.io/pypi/pyversions/coovts)](https://pypi.org/project/coovts/)
[![License](https://img.shields.io/badge/license-MIT-blue)](https://github.com/lgc2333/coovts/blob/main/LICENSE)

</div>

## ✨ Features

- ✨ Full type hints support with static type checking
- 🎯 Data validation and serialization using Pydantic
- 🔄 Async-first design with WebSocket communication
- 🎨 Easy-to-use event system for plugin development
- 🛡️ Built-in error handling and reconnection mechanisms

## 📖 Introduction

### Style at a glance

```python
import asyncio

from coovts.plugin import Plugin
from coovts.types import api, event

# no token yet: VTS asks the user once
plugin = Plugin("A Creative Plugin Name", "LgCuwukii☆")


@plugin.subscribe_event(event.ModelMovedEventData)
async def _(data: event.ModelMovedEventData):
    print(data.model_position)


# Requests need a session, so they belong in `on_authenticated`, which fires again after every reconnect;
# `call_api` is typed per request and returns that request's response model.
@plugin.on_authenticated
async def _():
    model = await plugin.call_api(api.CurrentModelRequest())
    print("current model:", model.model_name, model.model_id)


async def main() -> None:
    await plugin.run()


asyncio.run(main())
```

`plugin.run()` hands back the supervisor task; it must be awaited inside a running event loop,
because `asyncio.run()` builds its argument before the loop starts.

### Next

- Read the [guide in detail](https://github.com/lgc2333/coovts/blob/main/docs/guide/en/README.md)
- Read [`examples/basic.py`](https://github.com/lgc2333/coovts/blob/main/examples/basic.py) — the same plugin, with every logging hook filled in

Thanks for using it, and contributions are welcome 😊

## 💿 Install

You should use at least Python 3.12 to use this library.

```bash
pip install coovts
```

_or_

```bash
uv add coovts
```

## 📞 Contacts

- Telegram: [@lgc2333](https://t.me/lgc2333)
- QQ: 3076823485 / Group: [168603371](https://qm.qq.com/q/EikuZ5sP4G)
- Email: [lgc2333@126.com](mailto:lgc2333@126.com)
- Discord: [lgc2333](https://discordapp.com/users/810486152401256448) (Not active)

## 📝 Changelog

[CHANGELOG.md](https://github.com/lgc2333/coovts/blob/main/CHANGELOG.md)
