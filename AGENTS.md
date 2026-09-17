# coovts AGENTS.md

Python >= 3.12 library for writing VTube Studio plugins (async WebSocket + Pydantic v2).
Managed with uv; deps/logs/errors live in `pyproject.toml` and `coovts/errors.py`.

## Project Structure

```text
CONTEXT.md             domain glossary — words only, no decisions, no implementation
docs/adr/              architecture decisions, one per file (see Docs Rules)
coovts/
  plugin.py            Plugin: connect/auth/recv loops, hooks, event dispatch
  request.py           request-id <-> future correlation
  utils.py             run_sync
  py.typed             PEP 561 marker — shipped, do not delete
  types/
    shared.py          wire envelope + name-convention resolvers
    api/               VTS API request/response models
    event/             inbound event models (reuses wire models from api/)
    plugin_api.py      runtime ABC
    plugin_api.pyi     GENERATED — never hand-edit
scripts/
  generate_plugin_api.py   regenerates the .pyi
examples/
  basic.py                 canonical usage; README points here
tests*/                    does not exist yet (see Testing Rules)
.github/workflows/
  ci.yml                   ruff check + ruff format --check + basedpyright on every push/PR
  pypi-publish.yml         uv build + uv publish when a GitHub Release is published
```

## Commands

```bash
poe check        # basedpyright
poe lint         # ruff check
poe format       # ruff format
poe lint-fix     # ruff check --fix --unsafe-fixes
poe test         # pytest — pytest is not a declared dep yet, add it with pytest-asyncio first
poe gen-api      # regenerate coovts/types/plugin_api.pyi (after types/api|event changes)
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

- Every testcase function should have a short description as its docstring.

- Do not use fixtures that return values which cannot be precisely type-hinted, such as modules, as test function arguments; import those values locally instead for better type support.

## Commit

Use English conventional commit messages:

```text
type(optional scope): description

- List of change descriptions, focus one point per row

Optional footer(s)
```
