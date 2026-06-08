# Search

A-vorto provides full-text search via SQLite FTS5 with additional fuzzy matching.

## Full-Text Search (FTS5)

Uses SQLite's FTS5 extension for fast, relevance-ranked search.

```bash
A vorto serci "hello"
```

### Features

- **Relevance ranking**: Results sorted by relevance
- **Prefix matching**: "hel*" matches "hello", "helicopter"
- **Phrase search**: `"hello world"` for exact phrase
- **Boolean operators**: `AND`, `OR`, `NOT`

### Examples

```bash
# Basic search
A vorto serci "cœur"

# With filter
A vorto serci "hello" --lingvo en

# Multiple terms
A vorto serci "hello world"
```

## French Ligature Normalization

Search automatically normalizes French ligatures:

-œ → oe
- Œ → OE
- æ → ae
- Æ → AE

So searching "cœur" will find entries with "coeur".

## Fuzzy Matching

For typo tolerance, use fuzzy search:

```bash
A vorto serci "heelo" --fuzzy
```

Fuzzy matching uses Levenshtein distance. Install `rapidfuzz` for better performance:

```bash
pip install rapidfuzz
```

Without rapidfuzz, A-vorto falls back to Python's difflib (slower).

## Filters

Search can be filtered by:

| Filter | Option | Example |
|--------|--------|---------|
| Language | `--lingvo` | `--lingvo en` |
| Category | `--kategorio` | `--kategorio vorto` |
| Type | (via search) | via advanced search |

## Performance

FTS5 provides:
- O(log n) search time
- Incremental index updates
- Minimal disk space overhead

For large vocabularies (10,000+ entries), FTS5 remains fast.