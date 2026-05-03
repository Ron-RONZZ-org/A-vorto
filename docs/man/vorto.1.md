# VORTO(1) A-vorto User Manual

## NAME

vorto - personal wordbook microapp

## SYNOPSIS

**A vorto** [_command_] [_options_] [_arguments_]

## DESCRIPTION

A-vorto is a personal wordbook (vortaro) microapp for storing and managing vocabulary with definitions, usage examples, categories, and cross-references.

## COMMANDS

### list
List all word entries.

:   `A vorto list [-o FIELD] [-d] [-l LIMIT]`

### vidi
View a word entry.

:   `A vorto vidi UUID [--html] [--ref]`

### aldoni
Add a new word entry.

:   `A vorto aldoni TEXT [OPTIONS]`

### modifi
Modify a word entry.

:   `A vorto modifi UUID [OPTIONS]`

### forigi
Delete a word entry.

:   `A vorto forigi UUID [--hard]`

### serchi
Full-text search.

:   `A vorto serchi QUERY [--fuzzy] [-l LIMIT]`

### malfari
Undo the last operation.

:   `A vorto malfari`

### rubujo
List entries in trash.

:   `A vorto rubujo [-l LIMIT]`

### restaurigi
Restore an entry from trash.

:   `A vorto restaurigi UUID`

### senrubujigi
Empty trash.

:   `A vorto senrubujigi [-d DAYS]`

### importi
Import from JSON file.

:   `A vorto importi PATH [--password PASSWORD]`

### eksporti
Export to JSON/TOML file.

:   `A vorto eksporti PATH [-f FORMAT] [--password PASSWORD]`

## OPTIONS

### Global Options

:   `-h, --help`
:       Show help message

:   `--helpo`
:       Show help in Esperanto

### aldoni Options

:   `-l, --lingvo LANG`
:       Language (e.g., en, fr, eo)

:   `-k, --kategorio CAT`
:       Category (auto-detected if omitted)

:   `--tipo TYPE`
:       Type abbreviation(s), comma/semicolon-separated

:   `--temo THEME`
:       Theme

:   `--tono TONE`
:       Tonality (nf=informal, fo=formal, am=ambos)

:   `--difino DEF`
:       Definition with optional usage: difino:{uzo}

:   `--uzo USAGE`
:       Usage example (standalone)

:   `--etikedo TAG`
:       Tag in key:value format

:   `--autoro AUTHOR`
:       Author

:   `--verko WORK`
:       Work/source

:   `--nivelo LEVEL`
:       Proficiency level (0.0-5.0)

:   `--ligilo UUID`
:       Link to UUID(s)

### vidi Options

:   `-h, --html`
:       Open markdown as HTML preview in browser

:   `-r, --ref`
:       Show linked entries and references

### modifi Options

:   `-t, --teksto TEXT`
:       New word text

:   `--ligilo-add UUID`
:       Add link(s) to UUID(s)

:   `--ligilo-remove UUID`
:       Remove link(s) by UUID

:   `--clear-ligiloj`
:       Clear all links

### serchi Options

:   `-f, --fuzzy`
:       Enable fuzzy matching

:   `-l, --limit LIMIT`
:       Limit results (default: 20)

### forigi Options

:   `-H, --hard`
:       Permanent delete (no trash)

### eksporti Options

:   `-f, --format FORMAT`
:       Format: json or toml (default: json)

:   `-p, --password PASSWORD`
:       Encryption password

## TYPE ABBREVIATIONS

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

## EXAMPLES

```bash
# Add a word
A vorto aldoni "hello" --lingvo en --difino "saluton"

# Search
A vorto serchi "hello"

# View with references
A vorto vidi 952f2079 --ref

# Link entries
A vorto aldoni "world" --ligilo 952f2079

# Undo last operation
A vorto malfari
```

## FILES

:   `~/.local/share/A/vorto.db`
:       SQLite database with WAL mode

:   `~/.config/A/config.toml`
:       User configuration

## SEE ALSO

A-core(7), A(1)

## AUTHOR

Written by Ron.

## LICENSE

GPL-3.0-only

## BUGS

Report bugs at: https://github.com/Ron-RONZZ-org/A-vorto/issues