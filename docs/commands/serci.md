# vorto serci

Full-text search using SQLite FTS5.

## Usage

```bash
A vorto serci <QUERY> [OPTIONS]
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
| `--lingvo` | `-L` | Filter by language |
| `--kategorio` | `-k` | Filter by category (vorto/frazo/frazdaro) |
| `--tipo` | `-t` | Filter by type (su, aj, etc.) |
| `--temo` | `-m` | Filter by theme |
| `--tono` | `-T` | Filter by tonality (nf, fo, am) |

## Examples

```bash
# Basic full-text search
A vorto serci "hello"

# Search with language filter
A vorto serci "hello" --lingvo en

# Search with category filter
A vorto serci "hello" --kategorio vorto

# Search with multiple filters
A vorto serci "hello" --lingvo eo --kategorio frazo

# Fuzzy search (typo tolerance)
A vorto serci "heelo" --fuzzy

# Limit results
A vorto serci "hello" --limit 5

# Filter by type
A vorto serci "hello" --tipo su

# Filter by theme
A vorto serci "hello" --temo gramatiko

# Filter by tonality
A vorto serci "hello" --tono nf
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