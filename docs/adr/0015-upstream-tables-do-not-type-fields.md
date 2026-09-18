# Upstream tables are transcribed, and no wire field is typed by one

**Status**: accepted

VTube Studio ships the identifiers of its own API as source tables — `Files/ErrorID.cs`,
`HotkeyAction.cs`, `RestrictedRawKey.cs`, `Effects.cs` and `EffectConfigs.cs`. All five are
transcribed into `coovts/types/consts/`, keeping the upstream member names, their values and the
comments above them, with a link to the file and commit they came from at the top of each module.
`docs/references.md` records the sync point and how the transcription was checked. They exist so a
plugin author reads VTube Studio's own vocabulary instead of magic numbers, and so a member can be
read next to its upstream source.

None of them types a wire field. Payload fields stay `str`, `int` or `list[str]`, because VTube
Studio matches these identifiers case-insensitively with `_` and `-` ignored, and because a
transcription is a snapshot that can be older than the app answering: a closed type would turn a
spelling VTS accepts, or an ID a newer build added, into a decode error. `PermissionName` is the
same case — it records the two permissions upstream documents today, and no field is narrowed to it.

A table whose values travel as names is a `RawStrEnum`, whose `auto()` yields the member name so the
upstream spelling is written once; one whose values are numbers is an `IntEnum`. A member that
exists only to keep the table readable against its source is still transcribed and says so:
`HotkeyAction.Unset` is upstream's `-1` sentinel and documents that no payload carries it, and
`ErrorID.Event_TestEvent_TestMessageTooLong` repeats `EVENT_OFFSET`, which Python turns into an alias
rather than a second value.

The alternative was to put the tables in `cookit` or a package of their own; they are VTube Studio
protocol vocabulary, not general-purpose utilities, and a shared helper library must not carry one
application's semantics. Closing the fields on the enums was the other candidate, and it was
rejected above.

## Consequences

- Nothing in the library validates against these tables, so a caller that wants strictness checks
  membership itself. The runtime reads `ErrorID` only to recognise the authentication refusals that
  end a run (ADR-0016).
- A transcription may lag a newer VTS without breaking anything: an ID the library has no name for
  is still just a value.
- The list of tables is expected to grow with the upstream `Files/` directory; each addition is a
  transcription plus a row in `docs/references.md`, not a model.
