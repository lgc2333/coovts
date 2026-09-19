---
status: accepted
amends: ['0003', '0018']
---

# Unknown fields are kept, in the wire spelling

ADR-0018 settled how a payload model reads and writes the fields it declares: either spelling in,
the wire spelling out. Fields it does not declare were dropped in both directions.
`vts_base_model_config` now sets `extra="allow"`: an unmodelled key is kept in `model_extra` and
dumped exactly as it arrived, so a plugin can read a field the release in front of it predates, or
send one VTube Studio has just gained.

That is not hypothetical. The live check this library's transcription runs against a real VTube
Studio (see `docs/references.md`) found `ExpressionInfo.secondsSinceLastActive` in every expression
VTS 1.35.10 sent, and no upstream document mentions it; the same check is how the two ArtMesh group
fields were found missing from the models. Extras let a plugin bridge that gap without waiting for a
release.

The catch is that the alias generator does not touch them: it renames the fields a model declares,
and an extra key is written and read exactly as the caller wrote it. Building a payload for
something the models do not declare therefore means spelling the key the way the wire does
(`artMeshGroupIDExact`, not `art_mesh_group_id_exact`), and a typo in a request goes out as typed
instead of being dropped. The fields the audit found are modelled explicitly for that reason: an
extra key is an escape hatch, not the contract, and the guide says as much where field naming is
explained.

Rejected: keeping the drop, which leaves a field VTS already sends unreadable until the next release
and makes a request that uses one go out quietly without it; and `extra="forbid"`, which would fail
a frame carrying anything this library has not modelled, the opposite of a reader that tolerates
what it cannot know (ADR-0003).
