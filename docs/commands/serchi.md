# vorto serchi

Full-text search using SQLite FTS5.

## Usage

```bash
A vorto serchi <QUERY> [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<QUERY>` | Search query |

## Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--fuzzy` | `-f` | Enable fuzzy matching |
| `--limit` | `-l` | Limit results (default: 20) |

## Examples

```bash
# Basic full-text search
A vorto serchi "hello"

# Search with language filter
A vorto serchi "hello" --lingvo en

# Fuzzy search (typo tolerance)
A vorto serchi "heelo" --fuzzy

# Limit results
A vorto serchi "hello" --limit 5
```

## Search Features

- **Full-text matching**: Matches word text and definitions
- **French ligatures**: "cœur" matches "coeur", "œ" → "oe"
- **Language filter**: Filter by language code
- **Fuzzy matching**: Typo tolerance (requires `rapidfuzz` for speed)

## Installing rapidfuzz

For faster fuzzy matching:

```bash
pip install rapidfuzz
```

Without rapidfuzz, A-vorto falls back to difflib (slower but built-in).