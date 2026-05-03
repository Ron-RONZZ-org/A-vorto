# vorto list

List all word entries.

## Usage

```bash
A vorto list [OPTIONS]
```

## Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--order-by` | `-o` | Field to order by (default: teksto) |
| `--desc` | `-d` | Descending order |
| `--limit` | `-l` | Limit number of results |

## Examples

```bash
# List all entries (alphabetical)
A vorto list

# List by creation date (newest first)
A vorto list --order-by kreita_je --desc

# Limit to 10 entries
A vorto list --limit 10
```

## Fields for Ordering

- `teksto` - Word text
- `kreita_je` - Creation date
- `modifita_je` - Modification date
- `lingvo` - Language
- `kategorio` - Category