# Ligilo Text Resolution — Architectural Decision

## Summary
`vorto aldoni -L`/`--ligilo` (and `modifi --ligilo-add`/`--ligilo-remove`) should accept
text (teksto) input and resolve it to entry UUIDs, matching autish-legacy behavior.

## Issue
https://github.com/Ron-RONZZ-org/A-vorto/issues/41

## Architecture Decision

| Concern | Decision |
|---|---|
| Resolution logic location | `VortoService` (service layer) — new `resolve_ligilo_refs()` method |
| ec# support | Yes, with graceful fallback if A-encik not installed (dynamic import) |
| modifi scope | Yes — apply resolution to `--ligilo-add`/`--ligilo-remove` |
| A-core changes | None needed — `A.core.linking.sync_links_for_entry()` handles downstream |
| Error handling | Warn (`info()` non-fatal) + skip unresolvable refs |
| modify_helpers.py | No changes — remains pure data constructor, receives pre-resolved ligiloj |

## Resolution Logic (per ref)
1. Handle `ec#` → dynamic `import A_encik`, resolve to `ec#{uuid}`, store as-is if unresolvable
2. Handle `vt#` → strip prefix, resolve as UUID
3. Handle `#` → strip prefix, resolve as UUID
4. Treat as UUID → exact match + prefix match
5. Treat as text → case-insensitive exact `teksto` lookup
6. Ambiguous (multiple text matches) → warn + skip
7. Not found → warn + skip

## Files to Change
- `src/A_vorto/service.py` — add `resolve_ligilo_refs()`, modify `create()`
- `src/A_vorto/aldoni_cmd.py` — update `-L` help text
- `src/A_vorto/modifi_cmd.py` — update help text + call resolution before `_build_update_data()`
- `tests/test_service.py` — +10 test methods
