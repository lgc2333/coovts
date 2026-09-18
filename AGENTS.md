# coovts AGENTS.md

Python >= 3.12 library for writing VTube Studio plugins (async WebSocket + Pydantic v2).

## Project Structure

```text
README.md              user-facing intro; README.zh-cn.md mirrors it in Chinese
CHANGELOG.md           release notes users read (ADR-0012)
CONTEXT.md             domain glossary — words only, no decisions, no implementation
docs/adr/              architecture decisions, one per file (see Docs Rules)
docs/guide/            user-facing guide, en/ with a zh-cn/ mirror (see Docs Rules)
docs/backlog.md        deferred work — missing, not excluded (see Docs Rules)
coovts/
  plugin.py            Plugin: connect/auth/recv loops, hooks, event dispatch
  request.py           request-id <-> future correlation
  errors.py            exception hierarchy
  log.py               optional loguru shim — logging must not be a hard dependency
  utils/
    common.py          run_sync
    enum.py            RawStrEnum: a `StrEnum` whose `auto()` keeps the member name
  py.typed             PEP 561 marker — shipped, do not delete
  types/
    shared.py          wire envelope + name-convention resolvers
    api/               VTS API request/response models
    event/             inbound event models (reuses wire models from api/)
    consts/            error IDs and wire constant tables transcribed from upstream
    plugin_api.py      runtime ABC
    plugin_api.pyi     GENERATED — never hand-edit
scripts/
  generate_plugin_api.py   regenerates the .pyi (`--check` reports drift)
examples/
  basic.py                 canonical usage; README points here
tests_coovts/              pytest suite, mirrors the package layout (see Testing Rules)
.github/workflows/
  ci.yml                   ruff check + ruff format --check + stub check + basedpyright + pytest
  pypi-publish.yml         uv build + uv publish when a GitHub Release is published
```

## Commands

```bash
poe check         # basedpyright
poe lint          # ruff check
poe format        # ruff format
poe lint-fix      # ruff check --fix --unsafe-fixes
poe test          # pytest
poe coverage      # pytest with branch coverage of coovts
poe gen-api       # regenerate coovts/types/plugin_api.pyi (after types/api|event changes)
poe gen-api-check # fail if that stub is out of date (what CI runs)
```

If `poe` is not installed, ask user if we should install it: `uv tool install poethepoet`.

Type check, lint concurrently then format after your work done with any code change.
Only `poe` runs on the project venv; use `uv run` / `uv run --with` for anything else, never a global install.

## Rules

### Docs Rules

- `CONTEXT.md` is the domain glossary: canonical terms and one-line definitions, nothing else.
- `docs/adr/` holds one file per decision, numbered; add one when a decision is hard to reverse and would look arbitrary without the reason.
- Follow the `domain-modeling` skill for both (install it from GitHub `mattpocock/skills` if missing), and write in English like everywhere else here — except `docs/guide/zh-cn/`, `README.zh-cn.md` and `CHANGELOG.zh-cn.md`, which mirror their English counterparts for Chinese readers.

- `CHANGELOG.md` is the release notice users read: one section per release, plus an `Unreleased` one while work is pending; `0.0` promises nothing, so the number alone says nothing (ADR-0012). Keep `CHANGELOG.zh-cn.md` in step with it (same versions, same bullets).

- `docs/guide/{en,zh-cn}/` is the user-facing guide: one page per topic, the same pages in both languages, kept in sync (identical code blocks and anchors). It documents only what reading the code cannot tell you — runtime behaviour, failure modes, what is never retried — links `docs/adr/` for reasons, and points at upstream anchors for request/event field semantics instead of copying them.

- `docs/references.md` is the upstream sync record: where each transcribed constant and model came from, plus the current surface counts. Counts live there, never in an ADR.

- `docs/backlog.md` is the deferred work list: one entry per item, each saying what it is and what would trigger building it. No design discussion, and no item presented as excluded — an item moves into an ADR when it is decided against, and off the page once it is built.

### Structure Rules

- Keep related docs updated (like `AGENTS.md`s) when you make changes.

- Keep reference sources under `temp/references/`; use depth-1 clones for git repos.

- Store temp/intermediate files in `temp/<category>/` at the project root. Skills can override this rule.

- `coovts/types/plugin_api.pyi` is generated from `types/api` + `types/event` by `scripts/generate_plugin_api.py`; regenerate instead of editing it.

### Code Flavor Rules

- Format documentation (`*.md`) and structured data (`*.{json,yaml,toml}`, etc.) with `prettier` when it is available.

- Model fields and enum members are documented with a docstring written below them, never with a `#` comment.

- Payload models inherit `VTSBaseModel` (one shared `vts_base_model_config`), and frames coming off the wire are validated with `by_alias=True` — the config alone builds models from field names.

### Testing Rules

- Organize `tests*/` like node `.spec.ts` structure: each source file must have one correspondingly named test module.
- If the only test file for a module grows too large, it may be split into a directory named after the source module; files inside may use any `test_*.py` names.
- Reusable test scaffolding — fakes, mocks, transport stubs and shared helpers — lives under `tests*/utils/`, one module per concern; test modules import from there instead of redefining it or importing each other.

- Every testcase function should have a short description as its docstring.

- Keep test coverage as high as possible to avoid dead code. Code included in the current runtime's coverage scope should be covered unless it is version-specific, dependency-gated, or an intentional error path that is impractical to trigger safely.

- Do not use fixtures that return values which cannot be precisely type-hinted, such as modules, as test function arguments; import those values locally instead for better type support.

## Commit

Use English conventional commit messages:

```text
type(optional scope): description

- List of change descriptions, focus one point per row

Optional footer(s)
```
