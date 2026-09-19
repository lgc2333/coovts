# Requests

> [简体中文](../zh-cn/03-requests.md)

## Two entry points

```python
data = await plugin.call_api(api.CurrentModelRequest())
```

`call_api` is the one you normally use. For a `BaseModel` payload it derives both ends of the wire
protocol:

- **messageType** is the request model's class name — renaming the class renames the protocol, on
  purpose.
- **The response model** is the request class with `Request` swapped for `Response`; when that does
  not resolve, the library raises. A model can name its own answer instead, with the `resp_m` /
  `resp_t` class attributes.

Both derivations are defaults, not requirements, and any call can override either of them — including
"no response model at all":

```python
raw = await plugin.call_api(api.CurrentModelRequest(), response_model=None)  # raw dict
```

The four generic overloads at the bottom of the stub are what types that: pass
`response_model=SomeModel` and you get `SomeModel` back, pass `None` and you get `dict[str, Any]`.
`data` need not be a model either — then `message_type` has to be spelled out, since there is no class
name to fall back on, and `response_model` has to be given explicitly (a model, or `None` for the raw
dict).

`send_request` is the primitive underneath: it takes a whole `BaseRequest` — message type, API name
and version included — and derives nothing.

```python
from coovts.types import BaseRequest

request = BaseRequest(message_type="SomeUnmodelledRequest", data={"foo": 1})
raw = await plugin.send_request(request, response_model=None)  # unvalidated dict
```

## Timeouts

`Plugin(api_timeout=30)` sets the default deadline, 30 seconds. A single call can override it with
`api_timeout=`:

| Value   | Meaning                                  |
| ------- | ---------------------------------------- |
| omitted | Use the plugin's default                 |
| `10`    | Wait 10 seconds for this one             |
| `0`     | **Wait forever**, not "fail immediately" |
| `None`  | Wait forever                             |
| `...`   | Same as omitted                          |

An expired request raises `RequestTimeout`.

## What a failed request raises

Four exceptions, all raised at the `await`, all subclasses of `RequestError` (and so of `VTSError`):

| Exception         | Meaning                                                          | You can read                        |
| ----------------- | ---------------------------------------------------------------- | ----------------------------------- |
| `APIError`        | VTS refused the request                                          | `e.data.error_id`, `e.data.message` |
| `ValidationError` | The response did not decode into the target model                | `e.raw`, `e.model`                  |
| `RequestTimeout`  | No answer before the deadline                                    | —                                   |
| `NetworkError`    | There was no connection, or it died while waiting for the answer | —                                   |

`APIError.data.error_id` is a plain `int` (the wire's `errorID`); compare it against
`coovts.types.consts.ErrorID`, an `IntEnum`:

```python
from coovts.types.consts import ErrorID

try:
    ...
except APIError as e:
    if e.data.error_id == ErrorID.RequestRequiresPermission:
        ...
```

`ErrorID` is a transcription of upstream's `Files/ErrorID.cs`, each member carrying upstream's own
comment.

Two sharp edges:

- `RequestTimeout` subclasses the builtin `TimeoutError`, and therefore `OSError`. Your
  `except OSError` will quietly swallow it.
- A `ValidationError` can also come from an error response that fails to decode — either way, a
  payload that does not decode is a `ValidationError`, never something else.

## What happens to pending requests on a disconnect

They **fail immediately with `NetworkError`**, and are neither retried nor resumed; a reconnect
starts a fresh session and the caller decides whether a lost call is worth repeating. The one
exception is `stop()`, where pending requests end as `CancelledError`. The reasoning is in
[ADR-0008](../../adr/0008-request-correlation-and-error-surface.md).

One less obvious case: if the **envelope itself** fails to parse there is no `requestID` to match, so
the pending request is not failed at all — it waits out its timeout (`RequestTimeout`). The envelope
parse failure goes to `on_parse_data_error`.

## Escape hatches

For endpoints nobody has modelled yet — say upstream just added one — you do not wait for a library
release. A model of your own that inherits `coovts.types.shared.VTSBaseModel` takes the same path as a
library model: its class name is the messageType, and it carries the same naming rules and the same
validation.

```python
from coovts.types.shared import VTSBaseModel


class MyEndpointRequest(VTSBaseModel):
    some_field: int


raw = await plugin.call_api(MyEndpointRequest(some_field=1), response_model=None)
```

Three class attributes bend the naming conventions for a single model: `msg_t` (the message type, and
the event name), `resp_t` (a response model, by name) and `resp_m` (a response model, by class). A
payload that is not a model at all works too, as long as you hand over `message_type` and
`response_model` yourself.

## Field names and the wire

- **Build requests with snake_case field names; the dump spells them the wire way.** The config is
  `validate_by_name=True` with `serialize_by_alias=True`, so `ModelLoadRequest(model_id="...")` leaves
  as `modelID`. A dict that already carries wire keys goes in through `model_validate` — the
  constructor signature is built from field names, so `modelID=` would be a type error.
- **Neither spelling is an error.** Every model validates by field name and by alias, so a frame and a
  python dict both decode; wire data is camelCase because VTS sends camelCase. See
  [ADR-0018](../../adr/0018-aliases-validate-everywhere.md).
- **Unknown fields are dropped silently.** VTube Studio documents that it may add fields to existing
  payloads without a version bump, so extra keys are ignored rather than rejected — the price being
  that a new field stays invisible until someone models it. See
  [ADR-0003](../../adr/0003-model-config-and-tolerant-reader.md).

## Where the per-request field docs live

Upstream is the reference; this guide does not copy it. Find your module here:

| Module             | Upstream sections                                                                                                                                                                                                                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.info`         | [VTS statistics][s-stats] · [VTS folders][s-folders]                                                                                                                                                                                                                                                                    |
| `api.model`        | [Current model][s-cur-model] · [Available models][s-models] · [Loading a model by ID][s-load-model] · [Moving the model][s-move-model] · [Coordinate system][s-coord]                                                                                                                                                   |
| `api.hotkey`       | [Listing hotkeys][s-hotkeys] · [Triggering hotkeys][s-trigger]                                                                                                                                                                                                                                                          |
| `api.expression`   | [Expression states][s-expr-state] · [Activating/deactivating expressions][s-expr-act]                                                                                                                                                                                                                                   |
| `api.art_mesh`     | [ArtMesh list][s-artmesh-list] · [ArtMeshes at position][s-artmesh-pos] (beta) · [Tinting][s-tint] · [User selects ArtMeshes][s-select-artmesh]                                                                                                                                                                         |
| `api.param`        | [Face found][s-face] · [Tracking parameter list][s-params] · [One parameter][s-param-one] · [All Live2D parameters][s-param-all] · [Creating custom parameters][s-param-create] · [Deleting custom parameters][s-param-delete] · [Injecting values][s-param-inject] · [Several plugins on one parameter][s-param-multi] |
| `api.physics`      | [Reading physics settings][s-phys-get] · [Overriding physics settings][s-phys-set]                                                                                                                                                                                                                                      |
| `api.ndi`          | [NDI settings][s-ndi]                                                                                                                                                                                                                                                                                                   |
| `api.item`         | [Item list][s-items] · [Loading an item][s-item-load] ([custom data][s-item-custom]) · [Unloading an item][s-item-unload] · [Animation control][s-item-anim] · [Moving items][s-item-move] · [Within-model sorting][s-item-sort] · [Pinning to the model][s-item-pin]                                                   |
| `api.post_process` | [Listing post-processing effects][s-vfx-list] · [Setting them][s-vfx-set] ([usage advice][s-vfx-advice])                                                                                                                                                                                                                |
| `api.scene`        | [Lighting overlay color][s-scene-color]                                                                                                                                                                                                                                                                                 |
| `api.event`        | [Subscribing and unsubscribing][s-sub]                                                                                                                                                                                                                                                                                  |
| `api.auth`         | [Authentication][s-auth]                                                                                                                                                                                                                                                                                                |
| `api.permission`   | [Requesting permissions][s-perm] · [Available permissions][s-perm-list]                                                                                                                                                                                                                                                 |

The models marked beta (`ArtMeshAtPosition`, `ExpressionToggled`, `ArtMeshTracking`,
`ArtMeshOutline`) exist only on VTube Studio's public beta branch, and their docstrings say so.

## Next

[Events](./04-events.md) · [When things fail](./05-failures.md)

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
