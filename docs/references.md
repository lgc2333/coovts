# Upstream references

Where the transcribed parts of this library come from, and what the current surface covers away
from the upstream documents. Counts live here rather than in the ADRs: they are a snapshot of the
sync point below, not a decision.

## Sync point

|                  |                                                                     |
| ---------------- | ------------------------------------------------------------------- |
| Repository       | [DenchiSoft/VTubeStudio](https://github.com/DenchiSoft/VTubeStudio) |
| Branch           | `master`                                                            |
| Commit           | `0f46ef44b487fa17c8120db572ebd925924b93a3`                          |
| Fetched          | 2026-09-18                                                          |
| Verified against | VTube Studio 1.35.10, `apiVersion "1.0"`                            |

## What came from where

- `README.md` — the request/response API, source of `coovts/types/api/**`.
- `Events/README.md` — the event API, source of `coovts/types/event/**`.
- `Permissions/README.md` — the permission flow, source of `coovts/types/api/permission.py`.
- `Files/ErrorID.cs` → `coovts/types/consts/error_id.py`.
- `Files/HotkeyAction.cs` → `coovts/types/consts/hotkey_action.py`.
- `Files/Effects.cs` → `coovts/types/consts/effects.py`.
- `Files/EffectConfigs.cs` → `coovts/types/consts/effect_configs.py`.
- `Files/RestrictedRawKey.cs` → `coovts/types/consts/restricted_raw_key.py`.

The `consts` modules are transcriptions, not models: each one keeps a link to the file it came
from at the top, the member names stay in the upstream spelling, and the per-member docstrings
repeat the upstream comments. Keeping the spelling is safe because VTS accepts these IDs
case-insensitively with `_` and `-` ignored, so the wire form of a member is the member itself.

## Current surface

`poe gen-api` prints these numbers every time it runs, and `poe gen-api --dry-run` prints them
without writing the stub:

- 39 `call_api` overloads (plus 4 generic ones), generated from 106 models in `coovts/types/api`.
- 16 `subscribe_event` overloads, plus 1 for a model this package does not model and 1 for an event
  named by its wire name, generated from the 32 event config/data models in `coovts/types/event`. The
  overload for an unmodelled model defaults no `config`, so a call that forgot the config of an event
  that requires one falls on no overload at all instead of silently landing there; a named event
  defaults to an empty config instead, since nothing about it can be checked.
- `handle_event` is not generated: one generic method on `Plugin`, plus an overload for an event named
  by its wire name.

## How the transcription was checked

- Names, order and values of all five `consts` modules were diffed against their `.cs` files.
- All 29 `Effects` IDs and all 258 `EffectConfigs` IDs were compared as a set against the
  `PostProcessingListResponse` a real VTube Studio answered with both fill flags set, on the sync
  date: no difference in either direction.
- The three beta events and the beta `ArtMeshAtPositionRequest` were subscribed to / called against
  a stable VTS: `APIError` 950 (`Unknown API event type: ...`) and 7 (`Unknown messageType: ...`).
- A list-only `PermissionRequest` was answered with `grantSuccess: false`,
  `requestedPermission: ""` and a `permissions` array holding only the permissions VTS reports
  for this plugin.
