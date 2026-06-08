## Bug: `bulk_add_links` ImportError in `_migrate_links()`

### Root Cause
`A_vorto/service.py:_migrate_links()` called `bulk_add_links()` which was **never implemented** in `A.core.links`. This caused `ImportError` on every `vorto aldoni` (vaf) command because migration runs on first CRUD access.

### Secondary Bug Found
`service.py:get_references()` called `get_refs_in_field(item)` passing a **string** where the API expects `(dict, field_name)`. Changed to `parse_refs(item)` which correctly parses vt#/ec# references from a string.

### Fix
1. **A-core** (`src/A/core/links.py`): Added `LinksDB.bulk_add_links()` + module-level convenience `bulk_add_links()`
   - Batch inserts in single transaction
   - Skips self-links and duplicate violations
   - Default source_type="vorto" (matching the caller convention)
2. **A-vorto** (`src/A_vorto/service.py`): Changed `get_refs_in_field(item)` → `parse_refs(item)`

### Files Changed
- `/home/rongzhou/kodo/autish/A-core/src/A/core/links.py` - bulk_add_links
- `/home/rongzhou/kodo/autish/A-vorto/src/A_vorto/service.py` - parse_refs fix

### Commits
- A-core: `b760ced` feat: add bulk_add_links batch function for LinksDB
- A-vorto: `7964788` fix: use parse_refs instead of misused get_refs_in_field

### Verification
- A-core tests: 310 passed
- A-vorto tests: 94 passed
