"""Service layer for A-vorto using CRUDService."""

from __future__ import annotations

from typing import Any

from A.core.service import CRUDService

from A_vorto.data.storage import get_db, VORTO_FTS_CONFIG

_vorto_service: CRUDService | None = None


def get_service() -> CRUDService:
    """Get the singleton CRUDService for vorto table with FTS5."""
    global _vorto_service
    if _vorto_service is None:
        _vorto_service = CRUDService(get_db(), "vorto", fts_config=VORTO_FTS_CONFIG)
    return _vorto_service


__all__ = ["get_service"]