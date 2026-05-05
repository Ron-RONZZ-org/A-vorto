# Issue #21 — Duplicate Verification & Preview for `vorto aldoni`

## Decision Log

### Q1: `--yes`/`-y` flag?
**Yes.** Added to enable scripting/automation. Skips both duplicate prompts and save confirmation. Standard CLI UX pattern.

### Q2: Duplicate proposal flow?
Case-insensitive exact match on `teksto` via new `VortoService.find_by_teksto_exact()`. If found: show existing entry via `_show_entry()`, ask "Ĉu anstataŭigi?" (default no). If confirmed: `service.update(existing["uuid"], data)`.

### Q3: Where should logic live?
Split between layers:
- `VortoService.find_by_teksto_exact()` — data access
- `modify_helpers._show_preview()` — compact preview display
- `cli.py:aldoni()` — orchestration (check → branch → confirm → create/update)

## Key Design Principles Applied
1. Keep helpers pure (no `typer.confirm()` in helpers)
2. Orchestration visible in CLI layer
3. Minimal diff from existing structure
4. Testable via CliRunner's `input` parameter

## Implementation Plan
| File | Change |
|------|--------|
| `service.py` | +`find_by_teksto_exact()` |
| `modify_helpers.py` | +`_show_preview()` + `_PREVIEW_FIELDS` |
| `cli.py` | +`--yes` flag, restructure `aldoni()` |
| `tests/test_cli.py` | +5 test methods |
