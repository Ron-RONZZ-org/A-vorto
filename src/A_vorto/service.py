"""Service layer for A-vorto using CRUDService with links and references support."""

from __future__ import annotations

import json
from typing import Any

from A.core.service import CRUDService
from A.core.links import add_link, remove_link, get_outgoing, get_incoming, remove_all_for_entry
from A.core.references import get_refs_in_field, resolve as resolve_ref

from A_vorto.data.storage import get_db, VORTO_FTS_CONFIG

_vorto_service: VortoService | None = None

# Migration sentinel key
MIGRATION_SENTINEL = "vorto_links_migrated"


class VortoService:
    """Vorto service wrapping CRUDService with link sync and references support.
    
    Dual-role architecture:
    - ligiloj JSON column: source of truth for "what does this entry link to"
    - A.core.links: query index for O(1) bidirectional lookups
    """

    def __init__(self):
        self.crud = CRUDService(
            get_db(),
            "vorto",
            fts_config=VORTO_FTS_CONFIG,
            undo_size=10,
        )
        # Run migration once
        self._migrate_links()

    def _migrate_links(self) -> None:
        """One-time migration: sync existing ligiloj JSON to A.core.links."""
        from A.core.config import get_setting, set_setting
        
        if get_setting(MIGRATION_SENTINEL, False):
            return  # Already migrated
        
        db = get_db()
        entries = db.execute("SELECT uuid, ligiloj FROM vorto WHERE forigita_je IS NULL")
        
        for entry in entries:
            uuid = entry["uuid"]
            ligiloj = json.loads(entry.get("ligiloj") or "[]")
            for target_uuid in ligiloj:
                if target_uuid and uuid != target_uuid:
                    add_link("vorto", uuid, "vorto", target_uuid)
        
        set_setting(MIGRATION_SENTINEL, True)

    def _sync_links(self, entry: dict) -> None:
        """Sync ligiloj from entry JSON to A.core.links."""
        uuid = entry["uuid"]
        ligiloj = entry.get("ligiloj") or []
        
        # Clear existing links for this entry, then rebuild
        remove_all_for_entry("vorto", uuid)
        for target_uuid in ligiloj:
            if target_uuid and uuid != target_uuid:
                add_link("vorto", uuid, "vorto", target_uuid)

    def create(self, data: dict) -> dict:
        """Create entry and sync links."""
        entry = self.crud.create(data)
        self._sync_links(entry)
        return entry

    def update(self, uuid: str, data: dict) -> dict:
        """Update entry and sync links."""
        entry = self.crud.update(uuid, data)
        self._sync_links(entry)
        return entry

    def delete(self, uuid: str, soft: bool = True) -> None:
        """Delete entry and remove associated links."""
        self.crud.delete(uuid, soft=soft)
        remove_all_for_entry("vorto", uuid)

    def restore(self, uuid: str) -> dict | None:
        """Restore entry from trash and sync links."""
        entry = self.crud.restore(uuid)
        if entry:
            self._sync_links(entry)
        return entry

    def get(self, uuid: str) -> dict | None:
        """Get entry by UUID."""
        return self.crud.get(uuid)

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
        refs = []
        for field in ["difinoj", "uzoj"]:
            field_refs = get_refs_in_field(entry, field)
            for ref in field_refs:
                resolved = resolve_ref(ref.ref_type, ref.uuid)
                refs.append(resolved)
        return refs


def get_service() -> VortoService:
    """Get the singleton VortoService for vorto table with links and references."""
    global _vorto_service
    if _vorto_service is None:
        _vorto_service = VortoService()
    return _vorto_service


__all__ = ["get_service", "VortoService"]