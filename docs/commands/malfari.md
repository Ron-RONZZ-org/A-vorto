# vorto malfari

Undo the last operation.

## Usage

```bash
A vorto malfari
```

## Description

Undo the most recent add, modify, or delete operation. The undo stack keeps the last 10 operations.

## Examples

```bash
# Undo last operation
A vorto malfari
```

## Operations That Can Be Undone

- **add**: Restores deleted entry
- **modify**: Reverts to previous state
- **delete**: Restores entry from trash

## Limitations

- Only the last 10 operations can be undone
- Operations from before the last 10 are no longer available
- Undo is per-entry; batch operations are tracked individually