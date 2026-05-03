# Links & References

A-vorto supports bidirectional links between entries and cross-references using vt#uuid syntax.

## Bidirectional Links

Link entries together so changes propagate both ways.

### Adding Links

```bash
# Add entry with link
A vorto aldoni "world" --ligilo <uuid-of-hello>

# Add link to existing entry
A vorto modifi <uuid> --ligilo-add <target-uuid>

# Remove link
A vorto modifi <uuid> --ligilo-remove <target-uuid>

# Clear all links
A vorto modifi <uuid> --clear-ligiloj
```

### Viewing Links

Use `--ref` flag on `vidi` command:

```bash
A vorto vidi <uuid> --ref
```

This shows:
- **Elirantaj (outgoing)**: Entries this entry links to
- **Envenantaj (incoming)**: Entries that link to this entry (backlinks)

### How It Works

Links are stored in two places:
1. **ligiloj field** in entry (JSON array) - source of truth
2. **A.core.links** table - indexed for O(1) lookups

Changes to ligiloj automatically sync to the links table.

## Cross-References

Reference other entries using vt#uuid syntax in text fields.

### Syntax

- **Markdown link**: `[word](vt#uuid)`
- **Plain reference**: `vt#uuid`

The same syntax works for encik references:
- **Markdown link**: `[entry](ec#uuid)`
- **Plain reference**: `ec#uuid`

### Example

```bash
# Add entry with reference in definition
A vorto aldoni "greeting" --difino "See [hello](vt#952f2079) for basic greeting"
```

### Viewing References

The `--ref` flag also shows cross-references found in text fields:

```bash
A vorto vidi <uuid> --ref
```

Shows references as:
- ✓ [green] - entry exists
- ? [red] - entry not found

## Migration

Existing ligiloj data is migrated to the links table on first run. This is a one-time operation.