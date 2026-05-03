# vorto aldoni

Add a new word entry.

## Usage

```bash
A vorto aldoni <TEKSTO> [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<TEKSTO>` | The word text (required) |

## Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--lingvo` | `-l` | Language (e.g., en, fr, eo) |
| `--kategorio` | `-k` | Category (auto-detected if omitted) |
| `--tipo` | | Type abbreviation(s), comma/semicolon-separated |
| `--temo` | | Theme |
| `--tono` | | Tonality (nf=informal, fo=formal, am=ambos) |
| `--difino` | | Definition (can include usage: `difino:{uzo}`) |
| `--uzo` | | Usage example (standalone) |
| `--etikedo` | | Tag in key:value format |
| `--autoro` | | Author |
| `--verko` | | Work/source |
| `--nivelo` | | Proficiency level (0.0-5.0) |
| `--ligilo` | | Link to UUID(s) |

## Type Abbreviations

| Abbr. | Full Type |
|-------|-----------|
| su | substantivo (noun) |
| aj | adjektivo (adjective) |
| av | adverbo (adverb) |
| ve | verbo (verb) |
| vt | verbo-transitiva |
| vn | verbo-netransitiva |
| prep | prepozicio |
| konj | konjunkcio |
| inter | interjekcio |

## Examples

```bash
# Simple entry
A vorto aldoni "hello"

# With definition and language
A vorto aldoni "hello" --lingvo en --difino "saluton"

# With type and category
A vorto aldoni "hello" --tipo su --kategorio vorto

# With definition and usage
A vorto aldoni "hello" --difino "saluton:persona saluto" --uzo "hello world"

# With tags
A vorto aldoni "hello" --etikedo source:book --etikedo难度:中

# With links to other entries
A vorto aldoni "world" --ligilo 952f2079 abc12345

# Full example
A vorto aldoni "hello" --lingvo en --difino "saluton" --uzo "hello world" --tipo su,aj --nivelo 2.5
```