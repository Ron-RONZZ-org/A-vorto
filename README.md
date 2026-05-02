# A-vorto

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