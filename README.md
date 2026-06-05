# A-vorto

## Context

This module uses [A-workspace](https://github.com/Ron-RONZZ-org/A-workspace) as a **git submodule**:


```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/Ron-RONZZ-org/A-vorto.git
# Or if already cloned:
git submodule update --init --recursive
```

**DO NOT edit workspace/ directly** - see [A-workspace](https://github.com/Ron-RONZZ-org/A-workspace) for master context.


A-vorto - personal wordbook (vortaro) microapp

## Install

```bash
# Recommended — fast, reliable
pip install uv && uv pip install A-vorto

# Traditional
pip install A-vorto
```

Requires **A-core** (automatically installed as dependency).

## Usage

```bash
A vorto list              # List all word entries
A vorto vidi <uuid>       # View a word entry (--html for markdown preview)
A vorto serci <query>     # Full-text search (FTS5, --fuzzy for fuzzy match)
A vorto recenzi           # Interactive vocabulary review
A vorto recenzi-historio  # View review session history
A vorto aldoni <teksto>   # Add a new word entry
A vorto modifi <uuid>     # Modify a word entry
A vorto forigi <uuid>     # Delete (soft) or --hard (permanent)
A vorto malfari           # Undo last operation
A vorto rubujo            # List entries in trash
A vorto restaurigi <uuid>  # Restore from trash
A vorto senrubujigi       # Empty trash (--days N)
A vorto importi <path>    # Import from JSON (--password for encrypted)
A vorto eksporti <path>   # Export to JSON/TOML (--format json|toml --password)
```

## Search

A-vorto includes full-text search via SQLite FTS5:

- **Full-text search**: Matches words and definitions
- **French ligature support**: Search "cœur" finds "coeur" too
- **Filters**: By language (`-l`), category (`-k`), type (`-t`)
- **Fuzzy matching**: Typo tolerance (install `rapidfuzz` for speed)

```bash
# Full-text search
A vorto serci "cœur"

# With language filter
A vorto serci "hello" --lingvo en

# Date range filter (supports YYYYMMDD, MMDD, DD, or YYYY-MM-DD)
A vorto serci "hello" --dato-de 2026-01-01 --dato-gis 20261231

# Fuzzy search (requires: uv pip install rapidfuzz)
A vorto serci "heelo" --fuzzy
```

## Testing

```bash
cd A-vorto
uv venv .venv && uv pip install pytest pytest-mock typer rich --python .venv/bin/python
PYTHONPATH=../A-core/src:src .venv/bin/python -m pytest tests/
```

**125 tests passing** (test_cli.py, test_service.py, test_storage.py, test_utils.py, test_recenzi.py)

## Documentation

Full documentation available at: **https://a-vorto.readthedocs.io**

- **Read the Docs**: Installation, commands, features, API reference
- **Man pages**: `man vorto` (see `docs/man/vorto.1.md`)

## About

A-vorto is a plugin for the [A](https://github.com/Ron-RONZZ-org/A-core/) framework.

**A-vorto depends on A-core** for:
- Plugin discovery via entry points
- i18n (tr() for multilingual support)
- SQLite with WAL mode
- Shared utilities (error(), info(), run())

See the [A-core documentation](https://github.com/Ron-RONZZ-org/A-core/) for more on the framework.

## Migration from autish

A-vorto supports migration from autish:

```bash
A migri           # Run migrations (imports words)
```

| Legacy | Target | Description |
|--------|--------|-------------|
| vorto.db → vorto | A-vorto → vorto | Wordbook |

## History

A-vorto is based on [autish vorto](https://github.com/Ron-RONZZ-org/autish/) and is the reference implementation for A plugins.

## License

GPL-3.0-only
---

**Branch:** Use `main` for all development.
