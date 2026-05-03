# Import and Export

## vorto importi

Import word entries from JSON file.

```bash
A vorto importi <PATH> [--password PASSWORD]
```

| Argument | Description |
|----------|-------------|
| `<PATH>` | Path to import file |

| Option | Description |
|--------|-------------|
| `--password` | Decryption password for encrypted files |

### Example

```bash
# Import from JSON
A vorto importi words.json

# Import encrypted file
A vorto importi words.enc --password mysecret
```

---

## vorto eksporti

Export word entries to JSON or TOML file.

```bash
A vorto eksporti <PATH> [--format FORMAT] [--password PASSWORD]
```

| Argument | Description |
|----------|-------------|
| `<PATH>` | Path to export file |

| Option | Default | Description |
|--------|---------|-------------|
| `--format` | json | Format: json or toml |
| `--password` | | Encryption password |

### Example

```bash
# Export to JSON
A vorto eksporti backup.json

# Export to TOML (single entry)
A vorto eksporti entry.toml --format toml

# Export encrypted
A vorto eksporti backup.enc --password mysecret
```

## File Formats

### JSON

Export all entries as JSON array:
```json
[
  {"teksto": "hello", "lingvo": "en", "difinoj": ["saluton"]},
  {"teksto": "world", "lingvo": "en", "difinoj": ["mondo"]}
]
```

### TOML

Export single entry as TOML:
```toml
teksto = "hello"
lingvo = "en"
difinoj = ["saluton"]
```

## Encryption

Files can be encrypted with a password using AES-256-GCM. Encrypted files have `.enc` extension by convention but any extension works.

```bash
# Export with encryption
A vorto eksporti secure.json --password mypass

# Import encrypted file
A vorto importi secure.json --password mypass
```