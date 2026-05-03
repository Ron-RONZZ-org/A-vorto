# vorto forigi

Delete a word entry.

## Usage

```bash
A vorto forigi <UUID> [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<UUID>` | UUID of the entry to delete |

## Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--hard` | `-H` | Permanent delete (no trash) |

## Examples

```bash
# Soft delete (moves to trash)
A vorto forigi 952f2079

# Permanent delete
A vorto forigi 952f2079 --hard
```

## Behavior

- **Soft delete (default)**: Entry is moved to trash and can be restored
- **Permanent delete**: Entry is permanently removed and cannot be restored

## See Also

- [`vorto rubujo`](rubujo.md) - View trash
- [`vorto restaurigi`](rubujo.md#restaurigi) - Restore from trash
- [`vorto senrubujigi`](rubujo.md#senrubujigi) - Empty trash