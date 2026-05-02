"""Vorto data layer - SQLite storage."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from A import ensure_dirs as _ensure_dirs
from A.data.base import SQLiteDB

_DATA_DIR: Path = Path.home() / ".local" / "share" / "A"
_DB_FILE: Path = _DATA_DIR / "vorto.db"

_CREATE_VORTO = """
CREATE TABLE IF NOT EXISTS vorto (
    uuid TEXT PRIMARY KEY,
    teksto TEXT NOT NULL,
    lingvo TEXT,
    kategorio TEXT,
    tipo TEXT,
    temo TEXT,
    tono TEXT,
    nivelo REAL,
    difinoj TEXT NOT NULL DEFAULT '[]',
    uzoj TEXT NOT NULL DEFAULT '[]',
    etikedoj TEXT NOT NULL DEFAULT '{}',
    ligiloj TEXT NOT NULL DEFAULT '[]',
    autoro TEXT,
    verko TEXT,
    kreita_je TEXT NOT NULL,
    modifita_je TEXT NOT NULL
);
"""

_CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_vorto_teksto ON vorto(teksto);
CREATE INDEX IF NOT EXISTS idx_vorto_lingvo ON vorto(lingvo);
CREATE INDEX IF NOT EXISTS idx_vorto_kategorio ON vorto(kategorio);
"""


def ensure_dirs() -> None:
    """Ensure data directory exists."""
    _ensure_dirs(_DATA_DIR)


def get_db() -> SQLiteDB:
    """Get database connection."""
    ensure_dirs()
    db = SQLiteDB(_DB_FILE)
    db.execute(_CREATE_VORTO)
    for stmt in _CREATE_INDEXES.strip().split(";"):
        if stmt.strip():
            db.execute(stmt)
    return db


__all__ = ["ensure_dirs", "get_db"]