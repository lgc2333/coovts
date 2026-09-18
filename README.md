<!-- markdownlint-disable MD033 MD036 MD041 -->

<div align="center">

<a href="https://github.com/lgc2333/coovts">
  <img src="https://raw.githubusercontent.com/lgc2333/coovts/main/assets/coovts.svg" width="315" alt="CooVTS Logo">
</a>

# CooVTS

_✨ Another library for making VTube Studio plugins with Python ✨_

English | [简体中文](README.zh-cn.md)

[![CI](https://github.com/lgc2333/coovts/actions/workflows/ci.yml/badge.svg)](https://github.com/lgc2333/coovts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/lgc2333/coovts/branch/main/graph/badge.svg)](https://codecov.io/gh/lgc2333/coovts)
[![PyPI](https://img.shields.io/pypi/v/coovts)](https://pypi.org/project/coovts/)
[![Python versions](https://img.shields.io/pypi/pyversions/coovts)](https://pypi.org/project/coovts/)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

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

### Next

- Read the [guide in detail](./docs/guide/en/README.md)
- Read [`examples/basic.py`](./examples/basic.py) — the same plugin, with every logging hook filled in

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

There are no extras and no logging dependency: Pydantic and `websockets` are the whole runtime set,
and everything a plugin has to know arrives as a hook or an exception
([ADR-0011](./docs/adr/0011-dependency-set.md)).

## 📞 Contacts

- Telegram: [@lgc2333](https://t.me/lgc2333)
- QQ: 3076823485 / Group: [168603371](https://qm.qq.com/q/EikuZ5sP4G)
- Email: [lgc2333@126.com](mailto:lgc2333@126.com)
- Discord: [lgc2333](https://discordapp.com/users/810486152401256448) (Not active)

## 📝 Changelog

[CHANGELOG.md](./CHANGELOG.md)
