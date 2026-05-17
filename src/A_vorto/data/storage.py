"""Vorto data layer - SQLite storage."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from A import ensure_dirs as _ensure_dirs
from A.data.base import SQLiteDB, backup_db, health_check
from A.data.search import FTSConfig
from A.utils.normalize import fold_search_text

from A_vorto.data.migrate import migrate

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

_CREATE_SCHEMA_VERSION = """
CREATE TABLE IF NOT EXISTS _schema_version (
    version INTEGER PRIMARY KEY,
    applied_je TEXT NOT NULL
);
"""

_CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_vorto_teksto ON vorto(teksto);
CREATE INDEX IF NOT EXISTS idx_vorto_lingvo ON vorto(lingvo);
CREATE INDEX IF NOT EXISTS idx_vorto_kategorio ON vorto(kategorio);
"""


def ensure_dirs() -> None:
    """Ensure data directory exists."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_db() -> SQLiteDB:
    """Get database connection with health check and backup."""
    ensure_dirs()
    if not health_check(_DB_FILE):
        from A.data.base import repair_db as _repair
        _repair(_DB_FILE)
    backup_db(_DB_FILE)
    db = SQLiteDB(_DB_FILE)
    db.execute(_CREATE_VORTO)
    db.execute(_CREATE_SCHEMA_VERSION)
    for stmt in _CREATE_INDEXES.strip().split(";"):
        if stmt.strip():
            db.execute(stmt)
    migrate(db)
    return db


# FTS5 configuration for vorto full-text search
VORTO_FTS_CONFIG = FTSConfig(
    table="vorto",
    fts_columns=["teksto"],
    filter_columns=["lingvo", "kategorio", "tipo", "temo"],
    normalize={"teksto": fold_search_text},
)


__all__ = ["ensure_dirs", "get_db", "VORTO_FTS_CONFIG"]