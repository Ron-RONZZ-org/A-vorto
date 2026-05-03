# AGENTS.md — Rules for A-vorto
This file extends [A-workspace](./workspace/AGENTS.md).

This file extends root A-core AGENTS.md for the A-vorto plugin.

## Relationship to A-core

**A-vorto depends on A-core** for:
- `A` package imports (i18n, output, subprocess, SQLite)
- Plugin discovery via entry points
- Shared utilities
- **API Reference**: See [A-core AGENTS.md](https://github.com/Ron-RONZZ-org/A-core/blob/main/AGENTS.md#api-reference)

**All source code must import from `A`, never duplicate utilities.**

## Dependency on Other A Plugins

In autish, vorto and encik share data (`ligilo` relations). In A:

- **A-vorto should detect A-encik at runtime:**
  ```python
  try:
      import A_encik
  except ImportError:
      # Handle gracefully - offer to install
  ```

- **Never import at module load time** — detect at call time, not import time
- **Use dynamic imports** for optional cross-plugin features

## If You Need Something in Core

If you need a utility that should be in A-core:

1. **Search existing issues** on [A-core](https://github.com/Ron-RONZZ-org/A-core/issues)
2. **Create an issue** describing the need
3. **Wait for core enhancement** before implementing locally
4. **Use feature detection** when available

**Don't just add it locally** — the whole point of A is shared utilities.

## Architecture

```
src/A_vorto/
├── __init__.py       # Plugin exports
├── cli.py           # Typer app (11 commands)
├── service.py       # CRUDService with FTS5
├── utils.py         # Type maps, parsers, normalizers (TIPO_MAP, TONO_MAP, difino/uzo parsing, etikedoj, kategorio auto-detect)
└── data/
    └── storage.py  # SQLite (uses A.data.base + FTSConfig)
```

## Search

A-vorto uses A-core's FTS5 full-text search:

- Full-text search on `teksto` field
- Filters: `lingvo`, `kategorio`, `tipo`, `temo`
- French ligature normalization (œ→oe, æ→ae)
- Fuzzy matching via rapidfuzz (optional) or difflib fallback

```python
from A_vorto.service import get_service
svc = get_service()

# Full-text search (matches normalized form too)
svc.search_fts("cœur")  # matches "coeur" as well

# Fuzzy search (typo tolerance)
svc.search_fuzzy("heelo", threshold=0.8)

# Combined search
svc.search_advanced("query", fuzzy=True, filters={"lingvo": "fr"})
```

## Code Standards

1. Use `tr_multi()` for all user-facing strings (3-language: eo, en, fr)
2. Use `error()` for errors, `info()` for info
3. Type hints on all public functions
4. Docstrings on all public functions
5. Tests required for all modules
6. Use WAL mode for SQLite

## What to Avoid

- Don't duplicate A-core utilities
- Don't skip i18n (use `tr()`)
- Don't use `print()` — use `A` output functions
- Don't hardcode paths — use `A.core.paths`
- Don't implement utilities that should be in core

## Testing

```bash
cd A-vorto
uv venv .venv && uv pip install pytest pytest-mock typer rich --python .venv/bin/python
PYTHONPATH=../A-core/src:src .venv/bin/python -m pytest tests/
```

## Features

A-vorto integrates the following A-core features:

| Feature | CLI Command | A-core Module |
|---------|-------------|---------------|
| Undo system | `malfari` | `A.core.undo` |
| Soft-delete trash | `rubujo`, `restaurigi`, `senrubujigi` | `CRUDService.delete(soft=True)` |
| Import/Export | `importi`, `eksporti` | `A.core.import_`, `A.core.export` |
| Markdown preview | `vidi --html` | `A.core.markdown_html_view` |
| FTS5 search | `serchi` | `CRUDService.search_advanced()` |
| Fuzzy search | `serchi --fuzzy` | `CRUDService.search_fuzzy()` |
| Bidirectional links | `--ligilo` on `aldoni`/`modifi` | `A.core.links` (A-core #18) |
| Cross-references | `--ref` on `vidi` | `A.core.references` (A-core #19) |

## A-vorto specific features

| Feature | CLI | Implementation |
|---------|-----|----------------|
| Type normalization | `--tipo su,aj` | `utils.normalize_tipo()` maps abbreviations via TIPO_MAP |
| Tonality normalization | `--tono nf` | `utils.normalize_tono()` maps via TONO_MAP |
| Difinoj+Uzoj input | `--difino "def:{eg}"` | `utils.split_difino_uzo()` (3 syntax variants) |
| Etikedoj (tags) | `--etikedo key:val` | `utils.parse_etikedoj()` |
| Kategorio auto-detect | automatic on `aldoni` | `utils.detect_kategorio()` (vorto/frazo/frazdaro) |
| Multiline text normalization | automatic | `utils.normalize_multiline_text()` |
| Clear-* flags on `modifi` | `--clear-difinoj` etc. | Explicit reset of JSON arrays/null fields |

Implemented (A-core #18, #19):
- Bidirectional links via `--ligilo` on `aldoni`/`modifi` and `--ref` on `vidi`
- Cross-references `vt#uuid` parsed from text fields (difinoj, uzoj)

## Testing

```bash
cd A-vorto
uv venv .venv && uv pip install pytest pytest-mock typer rich --python .venv/bin/python
PYTHONPATH=../A-core/src:src .venv/bin/python -m pytest tests/
```

### Test Coverage

| Module | Tests | Description |
|--------|-------|-------------|
| `test_cli.py` | 7+ | CLI commands via CliRunner |
| `test_service.py` | 9 | CRUDService operations |
| `test_storage.py` | 5 | SQLite storage layer |
| `test_utils.py` | 56 | Type maps, parsers, normalizers |

**Total: 79 tests** (3 pre-existing FTS5 failures in test env)

## Documentation

- **Readthedocs**: https://a-vorto.readthedocs.io
- **Source**: `docs/` folder with commands/, features/, api.md

## Migration from autish

A-vorto supports migration from autish vorto.db:

| Legacy | Target | Description |
|--------|--------|-------------|
| vorto.db → vorto | A-vorto → vorto | Wordbook (487 entries) |

**CLI:**
```bash
A migri           # Run migrations
```

**Programmatic:**
```python
from A_vorto.data.migrate_from_autish import migrate
result = migrate()
```

Features:
- JSON field conversions (difinoj, uzoj, etikedoj, ligiloj)
- Preserves UUIDs and timestamps
- Idempotent

## Branch Convention

All A-* repos use `main` as the primary branch. Use `main` for all development.
