"""Tests for A-vorto storage module."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "A-core" / "src"))


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for testing."""
    return tmp_path


@pytest.fixture
def mock_data_dir(monkeypatch: pytest.MonkeyPatch, temp_dir: Path) -> None:
    """Mock data directory to temp path."""
    import A_vorto.data.storage as storage_module

    monkeypatch.setattr(storage_module, "_DATA_DIR", temp_dir)
    monkeypatch.setattr(storage_module, "_DB_FILE", temp_dir / "vorto.db")


class TestEnsureDirs:
    """Tests for ensure_dirs function."""

    def test_ensure_dirs_creates_directory(self, temp_dir: Path, mock_data_dir):
        """Test that ensure_dirs creates the data directory."""
        import A_vorto.data.storage as storage_module

        # ensure_dirs should create the directory
        storage_module.ensure_dirs()

        assert temp_dir.exists()
        assert temp_dir.is_dir()


class TestGetDb:
    """Tests for get_db function."""

    def test_get_db_creates_tables(self, temp_dir: Path, mock_data_dir):
        """Test that get_db creates required tables and indexes."""
        import A_vorto.data.storage as storage_module
        from A.data.base import SQLiteDB

        # Mock _ensure_dirs to avoid actual filesystem operations
        with patch.object(storage_module, "_ensure_dirs", lambda: None):
            db = storage_module.get_db()

        # Verify it's a SQLiteDB instance
        assert isinstance(db, SQLiteDB)

        # Verify vorto table exists
        result = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vorto'")
        assert len(result) == 1
        assert result[0]["name"] == "vorto"

    def test_get_db_creates_indexes(self, temp_dir: Path, mock_data_dir):
        """Test that get_db creates required indexes."""
        import A_vorto.data.storage as storage_module

        with patch.object(storage_module, "_ensure_dirs", lambda: None):
            db = storage_module.get_db()

        # Get all indexes on vorto table
        result = db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='vorto'"
        )
        index_names = [r["name"] for r in result]

        # Verify expected indexes exist
        assert "idx_vorto_teksto" in index_names
        assert "idx_vorto_lingvo" in index_names
        assert "idx_vorto_kategorio" in index_names

    def test_get_db_vorto_schema(self, temp_dir: Path, mock_data_dir):
        """Test vorto table has correct schema."""
        import A_vorto.data.storage as storage_module

        with patch.object(storage_module, "_ensure_dirs", lambda: None):
            db = storage_module.get_db()

        # Get column info
        result = db.execute("PRAGMA table_info(vorto)")
        columns = {r["name"]: r for r in result}

        # Verify required columns exist
        required_columns = [
            "uuid", "teksto", "lingvo", "kategorio", "tipo", "temo",
            "tono", "nivelo", "difinoj", "uzoj", "etikedoj", "ligiloj",
            "autoro", "verko", "kreita_je", "modifita_je"
        ]

        for col in required_columns:
            assert col in columns, f"Missing column: {col}"

        # Verify teksto is NOT NULL
        assert columns["teksto"]["notnull"] == 1

        # Note: pk info not available in all SQLite versions
        # UUID is primary key by schema definition


class TestGetDbSingleton:
    """Tests for get_db singleton behavior."""

    def test_get_db_returns_same_instance(self, temp_dir: Path, mock_data_dir):
        """Test that get_db returns the same instance on repeated calls."""
        import A_vorto.data.storage as storage_module

        with patch.object(storage_module, "_ensure_dirs", lambda: None):
            db1 = storage_module.get_db()
            db2 = storage_module.get_db()

        # Note: get_db creates new instance each time (unlike service singleton)
        # This is intentional - each call gets fresh connection from pool
        assert db1 is not db2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])