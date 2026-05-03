# API Reference

## Python API

### Service

```python
from A_vorto.service import get_service, VortoService

# Get service instance
service = get_service()

# CRUD operations
entry = service.get(uuid)
entries = service.list(limit=10)
entry = service.create({"teksto": "hello"})
entry = service.update(uuid, {"teksto": "world"})
service.delete(uuid)

# Link operations
links = service.get_linked_entries(uuid)
# Returns: {"outgoing": [Link], "incoming": [Link]}

# Reference operations
refs = service.get_references(entry)
# Returns: [ResolvedRef, ...]

# Undo
result = service.undo()
```

### Data Storage

```python
from A_vorto.data.storage import get_db, VORTO_FTS_CONFIG

db = get_db()
# db is A.data.SQLiteDB instance with FTS5 configured
```

## CLI Reference

For command-line usage, see [Commands](commands.md).

## Entry Fields

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | string | Unique identifier |
| `teksto` | string | Word text (required) |
| `lingvo` | string | Language code |
| `kategorio` | string | Category (vorto/frazo/frazdaro) |
| `tipo` | list | Word type(s) |
| `temo` | string | Theme |
| `tono` | string | Tonality (nf/fo/am) |
| `nivelo` | float | Proficiency level (0.0-5.0) |
| `difinoj` | list | Definitions |
| `uzoj` | list | Usage examples |
| `etikedoj` | dict | Tags as key:value |
| `ligiloj` | list | Linked UUIDs |
| `autoro` | string | Author |
| `verko` | string | Work/source |
| `kreita_je` | timestamp | Creation time |
| `modifita_je` | timestamp | Modification time |

## A-core Integration

A-vorto uses these A-core modules:

| Module | Purpose |
|--------|---------|
| `A.core.service.CRUDService` | Base CRUD operations |
| `A.core.links` | Bidirectional link storage |
| `A.core.references` | Cross-reference parsing |
| `A.core.i18n` | Multilingual strings |
| `A.core.import_` / `A.core.export` | Import/export |
| `A.core.markdown_html_view` | HTML preview |