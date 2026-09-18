# coovts AGENTS.md

Python >= 3.12 library for writing VTube Studio plugins (async WebSocket + Pydantic v2).
Managed with uv; deps in `pyproject.toml` (loguru is the optional `log` extra), errors in
`coovts/errors.py` and logging in `coovts/log.py`.

## Project Structure

```text
CONTEXT.md             domain glossary — words only, no decisions, no implementation
docs/adr/              architecture decisions, one per file (see Docs Rules)
coovts/
  plugin.py            Plugin: connect/auth/recv loops, hooks, event dispatch
  request.py           request-id <-> future correlation
  errors.py            exception hierarchy
  log.py               optional loguru shim — logging must not be a hard dependency
  utils.py             run_sync
  py.typed             PEP 561 marker — shipped, do not delete
  types/
    shared.py          wire envelope + name-convention resolvers
    api/               VTS API request/response models
    event/             inbound event models (reuses wire models from api/)
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
- Follow the `domain-modeling` skill for both (install it from GitHub `mattpocock/skills` if missing), and write in English like everywhere else here.

### Structure Rules

- Keep related docs updated (like `AGENTS.md`s) when you make changes.

- Keep reference sources under `temp/references/`; use depth-1 clones for git repos.

- Store temp/intermediate files in `temp/<category>/` at the project root. Skills can override this rule.

- `coovts/types/plugin_api.pyi` is generated from `types/api` + `types/event` by `scripts/generate_plugin_api.py`; regenerate instead of editing it.

### Testing Rules

- Organize `tests*/` like node `.spec.ts` structure: each source file must have one correspondingly named test module.
- If the only test file for a module grows too large, it may be split into a directory named after the source module; files inside may use any `test_*.py` names.
- Reusable test scaffolding — fakes, mocks, transport stubs and shared helpers — lives under `tests*/test_utils/`, one module per concern; test modules import from there instead of redefining it or importing each other.

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
