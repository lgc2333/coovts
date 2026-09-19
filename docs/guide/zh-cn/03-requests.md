# 发请求

> [English](../en/03-requests.md)

## 两个入口

```python
data = await plugin.call_api(api.CurrentModelRequest())
```

`call_api` 是常用入口。当 `data` 是 `BaseModel` 时，它替你推导线协议的两端：

- **messageType** = 请求模型的类名（所以改类名就是改协议，这是刻意的设计）。
- **响应模型** = 请求模型把 `Request` 换成 `Response` 找到的类；找不到就报错，也可以由模型自己的
  `resp_m` / `resp_t` 类属性指定。

这两个推导都只是默认值，不是限制：任何一次调用都能覆盖，甚至可以「不要响应模型」：

```python
raw = await plugin.call_api(api.CurrentModelRequest(), response_model=None)  # raw dict
```

stub 底部那四个泛型重载就是给这两种用法做类型的：传 `response_model=SomeModel` 就得到 `SomeModel`，
传 `None` 就得到 `dict[str, Any]`。`data` 也允许根本不是模型——这时 `message_type` 必须显式给出
（没有类名可退），`response_model` 也必须显式给（一个模型，或者给 `None` 拿原始字典）。

`send_request` 是下面那层原语：它收一个完整的 `BaseRequest`（message type、api name、api version 都在
里面），什么也不推导。

```python
from coovts.types import BaseRequest

request = BaseRequest(message_type="SomeUnmodelledRequest", data={"foo": 1})
raw = await plugin.send_request(request, response_model=None)  # unvalidated dict
```

## 超时

`Plugin(api_timeout=30)` 是全局限定时间，默认 30 秒。单个请求可以用 `api_timeout=` 覆盖：

| 传值   | 含义                     |
| ------ | ------------------------ |
| 不传   | 用 plugin 上的默认值     |
| `10`   | 这个请求等 10 秒         |
| `0`    | **无限等**，不是立即失败 |
| `None` | 无限等                   |
| `...`  | 同「不传」               |

超时抛 `RequestTimeout`。

有一个请求不受这个限定时间约束：库在没有 token 时发的 `AuthenticationTokenRequest`。它的答案是用户在
VTube Studio 弹窗上点一下，所以它会一直等下去，而不是被超时切断——被放弃的弹窗会在下一个会话里再问一次，
而用户还在看第一个弹窗（[ADR-0016](../../adr/0016-fatal-authentication-refusals-end-the-run.md)）。
`api_timeout` 管的是 VTS 不需要人参与就能回答的那些请求。

## 请求失败时抛什么

四个异常都在 `await` 处抛出，都继承 `RequestError`（进而 `VTSError`）：

| 异常              | 含义                                                   | 你能读到                            |
| ----------------- | ------------------------------------------------------ | ----------------------------------- |
| `APIError`        | VTS 明确拒绝了这次请求                                 | `e.data.error_id`、`e.data.message` |
| `ValidationError` | 响应解不成目标模型（VTS 换了字段、或推导错了响应模型） | `e.raw`、`e.model`                  |
| `RequestTimeout`  | 到点还没等到响应                                       | —                                   |
| `NetworkError`    | 发的时候就没有连接，或者连接在等响应时断掉             | —                                   |

`APIError.data.error_id` 是裸 `int`（线上的 `errorID`），拿它和 `coovts.types.consts.ErrorID`
（`IntEnum`）比就行：

```python
from coovts.types.consts import ErrorID

try:
    ...
except APIError as e:
    if e.data.error_id == ErrorID.RequestRequiresPermission:
        ...
```

`ErrorID` 是上游 `Files/ErrorID.cs` 的逐条转写表，每条都带上游注释。

两个容易咬人的细节：

- `RequestTimeout` 同时是内置 `TimeoutError` 的子类，也就**同时是 `OSError`**。你的
  `except OSError` 会顺手把它吃掉。
- `ValidationError` 也可能来自错误响应本身解不出来——无论如何，解不出来就是 `ValidationError`，
  不会变成别的异常。

## 断线时在途请求会怎样

**立刻以 `NetworkError` 失败**，不重试、不重发、不续传；重连只是重新开始一个新会话，调用方自己决定
要不要重来。唯一的例外是 `stop()`：那种情况下在途请求以 `CancelledError` 结束。理由见
[ADR-0008](../../adr/0008-request-correlation-and-error-surface.md)。

还有一个不那么直观的：如果**信封本身**解析不了，就没有 `requestID` 可以配对，那么那个在途请求不会被
立刻失败，而是一直等到超时（`RequestTimeout`）。信封解析失败会走 `on_parse_data_error`。

## 逃生舱

没被建模的端点（比如上游新加的）不用等库更新。自己写一个继承 `coovts.types.shared.VTSBaseModel` 的模型
就走和库内模型完全一样的路径：类名就是 messageType，命名规则和校验行为也都一样。

```python
from coovts.types.shared import VTSBaseModel


class MyEndpointRequest(VTSBaseModel):
    some_field: int


raw = await plugin.call_api(MyEndpointRequest(some_field=1), response_model=None)
```

三个类属性可以给单个模型改命名约定：`msg_t`（message type，同时也是事件名）、`resp_t`（按名字指定响应
模型）、`resp_m`（按类指定响应模型）。连模型都不是的载荷也行，只要你把 `message_type` 和
`response_model` 自己交出来。

## 字段命名与线层

- **构造请求时用蛇形字段名，输出照样是驼峰**：配置是 `validate_by_name=True` +
  `serialize_by_alias=True`，所以 `ModelLoadRequest(model_id="...")` 出去就是 `modelID`。手里已经是线上键名的
  字典走 `model_validate` 进去；构造函数签名由字段名生成，所以 `modelID=` 这种关键字是类型错误。
- **两种写法都不算错**：每个模型按字段名和别名都能校验，帧和 Python 字典都能解析；线上依然是驼峰，因为 VTS
  就发驼峰。见 [ADR-0018](../../adr/0018-aliases-validate-everywhere.md)。
- **未知字段原样走完一圈**：VTS 明确说可以在不升版本的情况下加字段，所以多出来的键会留在模型上
  （`model_extra`）并原样发出去，而不是被丢弃。别名生成器不会给它们改名，所以模型没有声明的字段必须按线上
  拼写（驼峰）写。见 [ADR-0020](../../adr/0020-unknown-fields-are-kept.md)。

## 各个请求的字段含义在哪

上游文档就是权威，本文不抄。按模块找：

| 模块               | 上游章节                                                                                                                                                                                                                                                 |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.info`         | [VTS 统计][s-stats] · [VTS 文件夹][s-folders]                                                                                                                                                                                                            |
| `api.model`        | [当前模型][s-cur-model] · [可用模型列表][s-models] · [按 ID 加载模型][s-load-model] · [移动模型][s-move-model] · [坐标系][s-coord]                                                                                                                       |
| `api.hotkey`       | [查询热键][s-hotkeys] · [触发热键][s-trigger]                                                                                                                                                                                                            |
| `api.expression`   | [表情状态][s-expr-state] · [激活/停用表情][s-expr-act]                                                                                                                                                                                                   |
| `api.art_mesh`     | [ArtMesh 列表][s-artmesh-list] · [按位置查询][s-artmesh-pos]（beta） · [染色][s-tint] · [让用户选择][s-select-artmesh]                                                                                                                                   |
| `api.param`        | [是否找到人脸][s-face] · [跟踪参数列表][s-params] · [单个参数值][s-param-one] · [全部 Live2D 参数][s-param-all] · [新建自定义参数][s-param-create] · [删除自定义参数][s-param-delete] · [注入参数值][s-param-inject] · [多插件抢同一参数][s-param-multi] |
| `api.physics`      | [读取物理设置][s-phys-get] · [覆盖物理设置][s-phys-set]                                                                                                                                                                                                  |
| `api.ndi`          | [NDI 设置][s-ndi]                                                                                                                                                                                                                                        |
| `api.item`         | [物品列表][s-items] · [加载物品][s-item-load]（[自定义数据][s-item-custom]） · [卸载物品][s-item-unload] · [动画控制][s-item-anim] · [移动物品][s-item-move] · [层间排序][s-item-sort] · [钉到模型上][s-item-pin]                                        |
| `api.post_process` | [后期效果列表][s-vfx-list] · [设置后期效果][s-vfx-set]（[使用建议][s-vfx-advice]）                                                                                                                                                                       |
| `api.scene`        | [光照叠加色][s-scene-color]                                                                                                                                                                                                                              |
| `api.event`        | [订阅与取消订阅][s-sub]                                                                                                                                                                                                                                  |
| `api.auth`         | [Authentication][s-auth]                                                                                                                                                                                                                                 |
| `api.permission`   | [请求权限][s-perm] · [权限列表][s-perm-list]                                                                                                                                                                                                             |

带 beta 标记的模型（`ArtMeshAtPosition`、`ExpressionToggled`、`ArtMeshTracking`、`ArtMeshOutline`）
只存在于 VTS 的公测分支，docstring 里都写明了。

## 下一步

[事件](./04-events.md) · [出错的时候](./05-failures.md)

[s-stats]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#getting-current-vts-statistics
[s-folders]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#getting-list-of-vts-folders
[s-cur-model]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#getting-the-currently-loaded-model
[s-models]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#getting-a-list-of-available-vts-models
[s-load-model]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#loading-a-vts-model-by-its-id
[s-move-model]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#moving-the-currently-loaded-vts-model
[s-coord]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#the-vts-coordinate-system
[s-hotkeys]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-list-of-hotkeys-available-in-current-or-other-vts-model
[s-trigger]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-execution-of-hotkeys
[s-expr-state]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-current-expression-state-list
[s-expr-act]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-activation-or-deactivation-of-expressions
[s-artmesh-list]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-list-of-artmeshes-in-current-model
[s-artmesh-pos]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-list-of-artmeshes-at-position
[s-tint]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#tint-artmeshes-with-color
[s-select-artmesh]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#asking-user-to-select-artmeshes
[s-face]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#checking-if-face-is-currently-found-by-tracker
[s-params]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-list-of-available-tracking-parameters
[s-param-one]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#get-the-value-for-one-specific-parameter-default-or-custom
[s-param-all]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#get-the-value-for-all-live2d-parameters-in-the-current-model
[s-param-create]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#adding-new-tracking-parameters-custom-parameters
[s-param-delete]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#delete-custom-parameters
[s-param-inject]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#feeding-in-data-for-default-or-custom-parameters
[s-param-multi]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#controlling-one-parameter-with-multiple-plugins
[s-phys-get]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#getting-physics-settings-of-currently-loaded-vts-model
[s-phys-set]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#overriding-physics-settings-of-currently-loaded-vts-model
[s-ndi]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#get-and-set-ndi-settings
[s-items]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#requesting-list-of-available-items-or-items-in-scene
[s-item-load]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#loading-item-into-the-scene
[s-item-custom]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#custom-data-items
[s-item-unload]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#removing-item-from-the-scene
[s-item-anim]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#controling-items-and-item-animations
[s-item-move]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#moving-items-in-the-scene
[s-item-sort]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#set-item-within-model-sorting-order
[s-item-pin]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#pin-items-to-the-model
[s-vfx-list]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#get-list-of-post-processing-effects-and-state
[s-vfx-set]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#set-post-processing-effects
[s-vfx-advice]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#general-usage-advice
[s-scene-color]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#getting-scene-lighting-overlay-color
[s-sub]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#subscribing-to-and-unsubscribing-from-events
[s-auth]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md#authentication
[s-perm]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Permissions/README.md#requesting-permissions
[s-perm-list]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Permissions/README.md#available-permissions
