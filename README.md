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
pip install A-vorto
```

Requires **A-core** (automatically installed as dependency).

## Usage

```bash
A vorto ls           # List all word entries
A vorto vidi <uuid>  # View a word entry
```

## Testing

```bash
cd A-vorto
uv venv .venv && uv pip install pytest pytest-mock typer rich --python .venv/bin/python
PYTHONPATH=../A-core/src:src .venv/bin/python -m pytest tests/
```

**23 tests passing** (test_cli.py, test_service.py, test_storage.py)

## About

A-vorto is a plugin for the [A](https://github.com/Ron-RONZZ-org/A-core/) framework.

**A-vorto depends on A-core** for:
- Plugin discovery via entry points
- i18n (tr() for multilingual support)
- SQLite with WAL mode
- Shared utilities (error(), info(), run())

See the [A-core documentation](https://github.com/Ron-RONZZ-org/A-core/) for more on the framework.

## History

A-vorto is based on [autish vorto](https://github.com/Ron-RONZZ-org/autish/) and is the reference implementation for A plugins.

## License

GPL-3.0-only