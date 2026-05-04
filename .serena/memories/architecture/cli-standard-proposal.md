# CLI Standard Proposal - Analysis for Issue #52

## Current State of All Modules

| Module | Standard-compliant | Deviations |
|--------|-------------------|------------|
| **A-vorto** | `aldoni`, `modifi`, `forigi`, `importi`, `eksporti` | `list`→`ls`, `restaurigi`→`restaŭrigi`, `serci`→`serĉi`, `malfari` not in proposal, trash via top-level cmds |
| **A-encik** | `ls`, `aldoni`, `modifi`, `forigi`, `serci`, `importi`, `eksporti` | `restaur`→`restaŭrigi`, trash via subcmd style (`rubujo ls`), extra: `grafo`, `repacigi`, `agordi`, `generi`, `semantika-serci` |
| **A-sistemo** | Domain-specific (no DB) | `ls` used in sub-apps, `aldoni`/`modifi`/`forigi`/`serci` in repo sub-app |
| **A-organizi** | Domain-specific | `aldoni`/`modifi`/`forigi`/`serci`/`ls` in sub-apps, has `malfari` |
| **A-lien** | Domain-specific | `aldoni`/`forigi`/`modifi`/`ls`/`serci`/`vidi` in sub-apps, has `malfari` |
| **A-tempo** | N/A (not CRUD-based) | Single callback, no subcommands |
| **A-medio** | Domain-specific | `ls`/`serci` in sub-apps, extra: `eljuti`, `ludi`, `kuketoj-helpo` |
| **A-sekurkopio** | `eksporti`, `importi` | No `ls`/CRUD commands, extra: `auto`, `daemon`, `historio` |

**Common cross-module patterns found:**
- `helpo` (not `helpi`) in `context_settings`
- `serci` (not `serĉi`) — all modules use `c` not `ĉ`
- `vidi` — not in proposal but used in vorto, encik, sistemo, organzi, lien
- `malfari` (undo) — in vorto, organzi, lien — supported by A-core's UndoManager
