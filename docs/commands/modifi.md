# vorto modifi

Modify an existing word entry.

## Usage

```bash
A vorto modifi <UUID> [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<UUID>` | UUID of the entry to modify |

## Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--teksto` | `-t` | New word text |
| `--lingvo` | `-l` | Language |
| `--kategorio` | `-k` | Category |
| `--tipo` | | Type |
| `--temo` | | Theme |
| `--tono` | | Tonality |
| `--difino` | | Definition(s) |
| `--uzo` | | Usage example(s) |
| `--etikedo` | | Tag(s) |
| `--autoro` | | Author |
| `--verko` | | Work/source |
| `--nivelo` | | Proficiency level |
| `--clear-difinoj` | | Clear all definitions |
| `--clear-uzoj` | | Clear all usage examples |
| `--clear-etikedoj` | | Clear all tags |
| `--clear-ligiloj` | | Clear all links |
| `--clear-tipo` | | Clear type |
| `--ligilo-add` | | Add link(s) to UUID(s) |
| `--ligilo-remove` | | Remove link(s) by UUID |

## Examples

```bash
# Change word text
A vorto modifi 952f2079 --teksto "greetings"

# Change definition
A vorto modifi 952f2079 --difino "new definition"

# Add a link
A vorto modifi 952f2079 --ligilo-add abc12345

# Remove a link
A vorto modifi 952f2079 --ligilo-remove abc12345

# Add and remove in same command
A vorto modifi 952f2079 --ligilo-add abc12345 --ligilo-remove def67890

# Clear all definitions
A vorto modifi 952f2079 --clear-difinoj

# Clear links
A vorto modifi 952f2079 --clear-ligiloj
```

## Modifying Lists

The `--difino` and `--uzo` options replace existing values. To add to existing values without replacing, use without `--clear-*`.

For links, use `--ligilo-add` and `--ligilo-remove` for atomic list operations.