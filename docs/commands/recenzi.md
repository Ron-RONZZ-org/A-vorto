# vorto recenzi

Interactive vocabulary review — builds on the same filter logic as `serci`.

## Usage

```bash
A vorto recenzi [OPTIONS] [TEKSTO]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `<TEKSTO>` | Text to filter entries (optional, all entries if omitted) |

## Options

| Option | Alias | Description |
|--------|-------|-------------|
| `--modo` | `-m` | Review mode: `difinoj`, `tajpu`, `multobla` (default: `difinoj`) |
| `--lingvo` | `-l` | Filter by language |
| `--tipo` | `-t` | Filter by type |
| `--temo` | | Filter by theme |
| `--tono` | | Filter by tonality |
| `--autoro` | `-a` | Filter by author |
| `--verko` | `-v` | Filter by work |
| `--nivelo-min` | | Minimum lexical level |
| `--nivelo-max` | | Maximum lexical level |
| `--dato-de` | | Filter by start date (YYYYMMDD, MMDD, DD, YYYY-MM-DD) |
| `--dato-gis` | | Filter by end date (same formats) |
| `--regex` | `-r` | Interpret text as regex |
| `--preciza` | `-p` | Disable fuzzy fallback |
| `--limo` | `-lo` | Max entries (default: 50) |
| `--ordo` | `-o` | Sort order: nivelo, dato, inversa-dato |

## Review Modes

### difinoj (default)
Shows the word, its definitions, and usage examples. Press Enter to advance through each entry. Self-paced — all entries count as correct.

### tajpu
Shows the definitions and usage examples. You type the word. The correct answer is shown after each response.

### multobla
Shows the definitions and usage examples. Choose from 4 options (1 correct + 3 distractors with the same `tipo`, randomly selected from the database).

## Examples

```bash
# Review all entries in flashcard mode
A vorto recenzi --modo tajpu

# Review French entries only
A vorto recenzi --lingvo fr --modo multobla

# Review entries added this month
A vorto recenzi --dato-de 20260601

# Review nouns only (10 entries)
A vorto recenzi --tipo substantivo --limo 10
```

## History

Review sessions are automatically saved. Manage history with the `recenzi-historio` subcommand:

```bash
# List recent sessions
A vorto recenzi-historio ls

# View session details
A vorto recenzi-historio vidi <session-uuid>

# Show global statistics
A vorto recenzi-historio statistiko

# Delete a session
A vorto recenzi-historio forigi <session-uuid>

# Clear all history
A vorto recenzi-historio malplenigi
```

## Session Data

Each session stores:
- Review mode
- Timestamp and duration
- Number of correct/wrong answers
- Per-word results (response given, response time)
