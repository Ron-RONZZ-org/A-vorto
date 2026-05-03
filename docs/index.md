# A-vorto — Personal Wordbook

A-vorto is a personal wordbook (vortaro) microapp for the A framework. Store and manage vocabulary with definitions, usage examples, categories, and cross-references.

## Quick Start

```bash
# Install
pip install A-vorto

# Add a word
A vorto aldoni "hello" --difino "saluton" --lingvo en

# Search
A vorto serchi "hello"

# View with references
A vorto vidi <uuid> --ref

# Link entries
A vorto aldoni "world" --ligilo <uuid-of-hello>
```

## Features

- **Full-text search** via SQLite FTS5
- **Bidirectional links** between entries
- **Cross-references** (vt#uuid syntax)
- **Undo system** with 10-operation history
- **Soft-delete** with trash and restore
- **Import/Export** JSON or TOML, optionally encrypted
- **Multilingual UI** (Esperanto, English, French)

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all entries |
| `vidi` | View entry details |
| `aldoni` | Add new entry |
| `modifi` | Modify entry |
| `forigi` | Delete entry |
| `serchi` | Full-text search |
| `malfari` | Undo last operation |
| `rubujo` | View trash |
| `restaurigi` | Restore from trash |
| `importi` | Import from file |
| `eksporti` | Export to file |

## See Also

- [Installation](installation.md)
- [Command Reference](commands.md)
- [Features](features/search.md)
- [API Reference](api.md)