"""Vorto data layer - SQLite storage."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from A.core.paths import data_dir
from A.core.backup_targets import BackupTarget
from A import ensure_dirs as _ensure_dirs
from A.data.base import SQLiteDB, backup_db, health_check
from A.data.search import FTSConfig
from A.utils.normalize import fold_search_text

from A_vorto.data.migrate import migrate

_db_instance: SQLiteDB | None = None

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
    data_dir().mkdir(parents=True, exist_ok=True)


def get_db(path: Path | None = None) -> SQLiteDB:
    """Get or create the shared database connection (singleton).

    All callers within the same process share one ``SQLiteDB`` instance,
    which uses one cached SQLite connection. This avoids WAL/SHM conflicts
    that occur when multiple connections access the same database file.

    The connection is lazily created on first call and cached in
    ``_db_instance``. Tests can reset the singleton by setting
    ``A_vorto.data.storage._db_instance = None`` in their teardown.

    Args:
        path: Optional explicit database path. If omitted, defaults to
            ``data_dir() / "vorto.db"`` (respects ``A_DIR`` env var).
    """
    global _db_instance
    if _db_instance is not None:
        return _db_instance

    db_path = path or data_dir() / "vorto.db"
    ensure_dirs()
    if not health_check(db_path):
        from A.data.base import repair_db as _repair
        _repair(db_path)
    backup_db(db_path)
    db = SQLiteDB(db_path)
    db.execute(_CREATE_VORTO)
    db.execute(_CREATE_SCHEMA_VERSION)
    for stmt in _CREATE_INDEXES.strip().split(";"):
        if stmt.strip():
            db.execute(stmt)
    migrate(db)
    _db_instance = db
    return db


# FTS5 configuration for vorto full-text search
VORTO_FTS_CONFIG = FTSConfig(
    table="vorto",
    fts_columns=["teksto"],
    filter_columns=["lingvo", "kategorio", "tipo", "temo"],
    normalize={"teksto": fold_search_text},
)


def get_backup_targets() -> list[BackupTarget]:
    """Return backup targets for A-vorto."""
    return [
        BackupTarget(
            path=data_dir() / "vorto.db",
            category="data",
            module="vorto",
            label="Vorto database",
        ),
    ]


__all__ = ["ensure_dirs", "get_db", "VORTO_FTS_CONFIG", "get_backup_targets"]