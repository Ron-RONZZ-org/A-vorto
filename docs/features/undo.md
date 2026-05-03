# Undo System

A-vorto tracks the last 10 operations for undo capability.

## Usage

```bash
A vorto malfari
```

## Operations Tracked

| Operation | Undo Action |
|-----------|-------------|
| `add` | Delete the added entry |
| `modify` | Restore previous state |
| `delete` (soft) | Restore from trash |

## How It Works

- Each operation is recorded with the old and new state
- The undo stack is stored in the database
- Operations are processed in LIFO order (last in, first out)

## Limitations

- **10 operations max**: Older operations are dropped
- **No redo**: Undo cannot be undone
- **Per-entry tracking**: Batch operations are tracked individually

## Example

```bash
# Accidentally deleted an entry
A vorto forigi 952f2079

# Undo the deletion
A vorto malfari
# Output: "Restored 952f2079"

# Entry is back in the main table
A vorto vidi 952f2079
```