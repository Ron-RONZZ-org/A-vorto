# Trash Commands

Manage deleted entries in the trash.

## vorto rubujo

List entries in trash.

```bash
A vorto rubujo [--limit N]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--limit` | 20 | Number of entries to show |

### Example

```bash
A vorto rubujo
A vorto rubujo --limit 50
```

---

## vorto restaurigi

Restore an entry from trash.

```bash
A vorto restaurigi <UUID>
```

| Argument | Description |
|----------|-------------|
| `<UUID>` | UUID of entry to restore |

### Example

```bash
A vorto restaurigi 952f2079
```

---

## vorto senrubujigi

Permanently delete entries from trash.

```bash
A vorto senrubujigi [--days N]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--days` | 30 | Delete entries older than N days |

### Example

```bash
# Delete entries older than 30 days
A vorto senrubujigi

# Delete entries older than 7 days
A vorto senrubujigi --days 7
```

## Notes

- Soft-deleted entries go to trash automatically
- Entries in trash can be restored or permanently deleted
- The trash auto-cleanup removes entries older than 30 days (configurable)