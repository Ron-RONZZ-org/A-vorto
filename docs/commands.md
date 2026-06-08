# Command Reference

All commands are prefixed with `A vorto`.

## Global Options

| Option | Description |
|--------|-------------|
| `-h, --help` | Show help |
| `--helpo` | Show help in Esperanto |

## Commands

| Command | Description |
|---------|-------------|
| [`list`](commands/list.md) | List all word entries |
| [`vidi`](commands/vidi.md) | View entry details |
| [`aldoni`](commands/aldoni.md) | Add new entry |
| [`modifi`](commands/modifi.md) | Modify entry |
| [`forigi`](commands/forigi.md) | Delete entry |
| [`serci`](commands/serci.md) | Full-text search with date filters |
| [`recenzi`](commands/recenzi.md) | Interactive vocabulary review |
| [`recenzi-historio`](commands/recenzi.md#history) | Review session history |
| [`malfari`](commands/malfari.md) | Undo last operation |
| [`rubujo`](commands/rubujo.md) | View trash |
| [`restaurigi`](commands/rubujo.md#restaurigi) | Restore from trash |
| [`senrubujigi`](commands/rubujo.md#senrubujigi) | Empty trash |
| [`importi`](commands/import-export.md) | Import from file |
| [`eksporti`](commands/import-export.md) | Export to file |

## Quick Reference

```bash
# View all entries
A vorto list

# Add entry with full details
A vorto aldoni "word" --lingvo en --difino "definition" --uzo "example" --tipo su,aj

# View with links and references
A vorto vidi <uuid> --ref

# Link entries
A vorto modifi <uuid> --ligilo-add <target-uuid>

# Search with fuzzy matching
A vorto serci "word" --fuzzy
```