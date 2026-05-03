"""Migration from autish vorto.db to A-vorto.

Run with:
    from A_vorto.data.migrate_from_autish import migrate
    
    result = migrate()
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from A_vorto.data.storage import get_db


# Legacy autish data path
_LEGACY_DIR = Path.home() / ".local" / "share" / "autish"
_LEGACY_DB = _LEGACY_DIR / "vorto.db"


def migrate() -> dict:
    """Migrate words from autish vorto.db to A-vorto.
    
    Returns:
        Dict with migration results
    """
    if not _LEGACY_DB.exists():
        return {"skipped": True, "reason": "No legacy data found"}
    
    # Connect to A-vorto DB
    target = get_db()
    
    migrated = 0
    errors = []
    
    # Connect to legacy DB
    legacy = sqlite3.connect(str(_LEGACY_DB))
    legacy.row_factory = sqlite3.Row
    
    # Migrate words
    rows = legacy.execute("SELECT * FROM vorto").fetchall()
    
    for row in rows:
        try:
            # Parse JSON fields
            difinoj = _parse_json_field(row, "difinoj")
            uzoj = _parse_json_field(row, "uzoj")
            etikedoj = _parse_json_field(row, "etikedoj")
            ligiloj = _parse_json_field(row, "ligiloj")
            
            # Insert into A-vorto
            now = datetime.now(timezone.utc).isoformat()
            target.execute(
                """INSERT INTO vorto (
                    uuid, teksto, lingvo, kategorio,
                    tipo, temo, tono, nivelo,
                    difinoj, uzoj, etikedoj, ligiloj,
                    autoro, verko, kreita_je, modifita_je
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    row["uuid"],
                    row["teksto"],
                    row["lingvo"],
                    row["kategorio"],
                    row["tipo"],
                    row["temo"],
                    row["tono"],
                    row["nivelo"],
                    json.dumps(difinoj),
                    json.dumps(uzoj),
                    json.dumps(etikedoj),
                    json.dumps(ligiloj),
                    row["autoro"],
                    row["verko"],
                    now,
                    now,
                ),
            )
            
            migrated += 1
            
        except Exception as e:
            errors.append(f"{row.get('uuid', 'unknown')}: {e}")
    
    legacy.close()
    
    return {
        "source_rows": len(rows),
        "migrated_rows": migrated,
        "errors": errors,
    }


def _parse_json_field(row: sqlite3.Row, field: str) -> dict | list:
    """Parse a JSON field."""
    val = row[field]
    if val:
        try:
            return json.loads(val)
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


__all__ = ["migrate"]