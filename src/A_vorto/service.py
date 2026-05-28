"""Service layer for A-vorto using CRUDService with links and references support."""

from __future__ import annotations

import json
from typing import Any

from A import serialize_json_columns
from A.core.service import CRUDService
from A.core.links import remove_link, get_outgoing, get_incoming, remove_all_for_entry
from A.core.references import get_refs_in_field, resolve as resolve_ref
from A.core.linking import sync_links_for_entry

from A_vorto.data.storage import get_db, VORTO_FTS_CONFIG

_vorto_service: VortoService | None = None

# Migration sentinel key
MIGRATION_SENTINEL = "vorto_links_migrated"

# JSON columns that need serialization to string for SQLite
JSON_COLUMNS = ("difinoj", "uzoj", "etikedoj", "ligiloj")


class VortoService:
    """Vorto service wrapping CRUDService with link sync and references support.

    The ``CRUDService`` (and thus the database connection) is created
    lazily on first access so that module-level ``get_service()`` does
    **not** connect to the real database at import time.  Tests that
    redirect ``A_DIR`` or reset singletons can safely import the module
    without side effects.

    Dual-role architecture:
    - ligiloj JSON column: source of truth for "what does this entry link to"
    - A.core.links: query index for O(1) bidirectional lookups
    """

    def __init__(self):
        self._crud = None
        self._migrated = False

    @property
    def crud(self):
        """Lazy CRUDService — database connection on first access."""
        if self._crud is None:
            self._crud = CRUDService(
                get_db(),
                "vorto",
                fts_config=VORTO_FTS_CONFIG,
                undo_size=10,
            )
        # Run migration once
        if not self._migrated:
            self._migrate_links()
            self._migrated = True
        return self._crud

    def _migrate_links(self) -> None:
        """One-time migration: sync existing ligiloj JSON to A.core.links.

        Batches all links into a single transaction for efficiency.
        """
        from A.core.config import get_setting, set_setting
        from A.core.links import bulk_add_links

        if get_setting(MIGRATION_SENTINEL, False):
            return  # Already migrated

        db = get_db()
        entries = db.execute(
            "SELECT uuid, ligiloj FROM vorto WHERE forigita_je IS NULL"
        )

        pairs: list[tuple[str, str]] = []
        for entry in entries:
            uuid = entry["uuid"]
            ligiloj = json.loads(entry.get("ligiloj") or "[]")
            for target_uuid in ligiloj:
                if target_uuid and uuid != target_uuid:
                    pairs.append((uuid, target_uuid))

        if pairs:
            inserted = bulk_add_links(pairs, source_type_default="vorto")
        else:
            inserted = 0

        set_setting(MIGRATION_SENTINEL, True)

    @staticmethod
    def _resolve_uuid(uuid: str) -> str | None:
        """Resolve a potentially short or #-prefixed UUID to a full UUID.

        Strips leading ``#`` if present, then tries exact match first,
        falling back to prefix match. Returns the full UUID string
        or ``None`` if no entry is found.
        """
        raw = uuid[1:] if uuid.startswith("#") else uuid
        entry = get_service().get(raw)
        return entry["uuid"] if entry else None

    def _sync_links(self, entry: dict) -> None:
        """Sync ligiloj from entry JSON + inline refs to A.core.links."""
        uuid = entry["uuid"]
        ligiloj = entry.get("ligiloj") or []

        # Ensure ligiloj is a list (may be JSON string from DB)
        if isinstance(ligiloj, str):
            try:
                ligiloj = json.loads(ligiloj) if ligiloj.strip() else []
            except (json.JSONDecodeError, TypeError):
                ligiloj = []

        sync_links_for_entry(
            uuid=uuid,
            source_type="vorto",
            text_fields={
                "difinoj": entry.get("difinoj") or [],
                "uzoj": entry.get("uzoj") or [],
                "verko": entry.get("verko") or "",
                "temo": entry.get("temo") or "",
            },
            explicit_links=ligiloj if isinstance(ligiloj, list) else [],
        )

    def create(self, data: dict) -> dict:
        """Create entry and sync links."""
        # Serialize JSON columns before passing to CRUDService
        serialized = serialize_json_columns(data, JSON_COLUMNS)
        entry = self.crud.create(serialized)
        self._sync_links(entry)
        return entry

    def update(self, uuid: str, data: dict) -> dict:
        """Update entry and sync links.

        Resolves short or ``#``-prefixed UUIDs to full UUID first.
        """
        resolved = self._resolve_uuid(uuid)
        if not resolved:
            raise ValueError(f"Entry not found: {uuid}")
        serialized = serialize_json_columns(data, JSON_COLUMNS)
        entry = self.crud.update(resolved, serialized)
        self._sync_links(entry)
        return entry

    def delete(self, uuid: str, soft: bool = True) -> None:
        """Delete entry and remove associated links.

        Resolves short or ``#``-prefixed UUIDs to full UUID first.
        """
        resolved = self._resolve_uuid(uuid)
        if not resolved:
            return  # Nothing to delete
        self.crud.delete(resolved, soft=soft)
        remove_all_for_entry("vorto", resolved)

    def restore(self, uuid: str) -> dict | None:
        """Restore entry from trash and sync links.

        Resolves short or ``#``-prefixed UUIDs to full UUID first.
        """
        resolved = self._resolve_uuid(uuid)
        if not resolved:
            return None
        entry = self.crud.restore(resolved)
        if entry:
            self._sync_links(entry)
        return entry

    def get(self, uuid: str) -> dict | None:
        """Get entry by UUID, stripping optional ``#`` prefix.

        Tries exact match first, then prefix match for short UUIDs.
        """
        raw = uuid[1:] if uuid.startswith("#") else uuid
        entry = self.crud.get(raw)
        if entry:
            return entry
        # Prefix match fallback for short UUIDs
        from A_vorto.data.storage import get_db
        db = get_db()
        row = db.execute_one(
            "SELECT * FROM vorto WHERE uuid LIKE ? AND forigita_je IS NULL",
            (f"{raw}%",),
        )
        return dict(row) if row else None

    def _resolve_uuid(self, uuid: str) -> str | None:
        """Resolve a short or ``#``-prefixed UUID to its full form.

        Returns the full UUID string, or ``None`` if no matching entry exists.
        """
        entry = self.get(uuid)
        return entry["uuid"] if entry else None

    def get_by_id(self, uuid: str) -> dict | None:
        """Get entry by UUID (alias for get)."""
        return self.crud.get(uuid)

    def list(self, **kw) -> list[dict]:
        """List entries."""
        return self.crud.list(**kw)

    def get_trash(self, **kw) -> list[dict]:
        """Get trash entries."""
        return self.crud.get_trash(**kw)

    def empty_trash(self, **kw) -> int:
        """Empty trash."""
        return self.crud.empty_trash(**kw)

    def undo(self) -> dict | None:
        """Undo last operation."""
        return self.crud.undo()

    def search_advanced(self, **kw) -> list[dict]:
        """Search entries."""
        return self.crud.search_advanced(**kw)

    def get_linked_entries(self, uuid: str) -> dict[str, list]:
        """Get linked entries (both outgoing and incoming).
        
        Returns:
            dict with 'outgoing' and 'incoming' lists of Link objects
        """
        return {
            "outgoing": get_outgoing("vorto", uuid),
            "incoming": get_incoming("vorto", uuid),
        }

    def get_references(self, entry: dict) -> list:
        """Get cross-references from text fields (difinoj, uzoj).
        
        Parses vt#uuid and ec#uuid references in entry text fields
        and resolves them to entry data.
        
        Returns:
            list of ResolvedRef objects
        """
        from A.core.references import get_refs_in_field
        refs = []
        for field in ("difinoj", "uzoj"):
            field_val = entry.get(field) or []
            if isinstance(field_val, list):
                for item in field_val:
                    refs.extend(get_refs_in_field(item or ""))
        return refs

    def find_by_text_prefix(self, text: str) -> dict | None:
        """Find entry by text prefix (case-insensitive).
        
        Args:
            text: Text to search for (prefix match, case-insensitive)
            
        Returns:
            First matching entry or None
        """
        # Use SQLite LIKE for prefix match
        db = get_db()
        row = db.execute_one(
            "SELECT * FROM vorto WHERE LOWER(teksto) LIKE ? ORDER BY kreita_je DESC LIMIT 1",
            (f"{text.lower()}%",),
        )
        return dict(row) if row else None


def get_service() -> VortoService:
    """Get the singleton VortoService for vorto table with links and references."""
    global _vorto_service
    if _vorto_service is None:
        _vorto_service = VortoService()
    return _vorto_service


__all__ = ["get_service", "VortoService"]