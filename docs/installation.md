# Installation

## Requirements

- Python 3.11+
- A-core (automatically installed as dependency)

## Install from PyPI

```bash
pip install A-vorto
```

## Install from Source

```bash
git clone https://github.com/Ron-RONZZ-org/A-vorto.git
cd A-vorto
pip install -e .
```

## Install with A Framework

A-vorto is part of the A framework. Install the full framework:

```bash
pip install A-core
```

This includes all A plugins (vorto, tempo, encik, etc.).

## Verify Installation

```bash
A vorto --help
```

## Updating

```bash
pip install --upgrade A-vorto
```

## Dependencies

**Required:**
- `typer[rich]` - CLI framework
- `rich` - Terminal formatting
- `A-core` - Framework

**Optional (for better performance):**
- `rapidfuzz` - Faster fuzzy matching

Install with:
```bash
pip install A-vorto[dev]
```