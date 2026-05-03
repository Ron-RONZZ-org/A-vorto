# vorto vidi

View a word entry by UUID.

## Usage

```bash
A vorto vidi <UUID> [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<UUID>` | UUID of the entry to view (or partial UUID prefix) |

## Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--html` | `-h` | Open markdown as HTML preview in browser |
| `--ref` | `-r` | Show linked entries and cross-references |

## Examples

```bash
# View entry
A vorto vidi 952f2079

# View with HTML preview
A vorto vidi 952f2079 --html

# View with links and references
A vorto vidi 952f2079 --ref

# View with HTML and references
A vorto vidi 952f2079 --html --ref
```

## Output Fields

- UUID
- Teksto (word text)
- Lingvo (language)
- Kategorio (category)
- Tipo (type)
- Temo (theme)
- Tono (tonality)
- Nivelo (proficiency level)
- Difinoj (definitions)
- Etikedoj (tags)
- Ligiloj (links)
- Kreita (created)
- Modifita (modified)