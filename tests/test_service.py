"""Tests for A-vorto service module."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "A-core" / "src"))

from A.core.service import CRUDService


class TestGetService:
    """Tests for get_service function."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up test environment (isolation handled by conftest)."""
        yield

    def test_get_service_wraps_crudservice(self):
        """Test that get_service returns VortoService wrapping CRUDService."""
        from A_vorto.service import get_service

        service = get_service()
        assert hasattr(service, "crud")
        assert isinstance(service.crud, CRUDService)

    def test_get_service_singleton(self):
        """Test that get_service returns singleton."""
        from A_vorto.service import get_service

        s1 = get_service()
        s2 = get_service()

        # Should be the same instance
        assert s1 is s2


class TestVortoServiceIntegration:
    """Integration tests for vorto CRUDService (requires DB)."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up test environment (isolation handled by conftest)."""
        yield

    @pytest.fixture
    def service(self):
        """Create service with test DB."""
        from A_vorto.service import get_service
        return get_service()

    def test_create_entry(self, service):
        """Test creating an entry."""
        data = {
            "teksto": "testword",
            "lingvo": "eo",
            "kategorio": "noun",
        }

        entry = service.create(data)

        assert "uuid" in entry
        assert entry["teksto"] == "testword"
        assert entry["lingvo"] == "eo"

    def test_get_entry(self, service):
        """Test getting an entry."""
        data = {
            "teksto": "getword",
            "lingvo": "en",
        }

        created = service.create(data)
        uuid = created["uuid"]

        entry = service.get(uuid)

        assert entry is not None
        assert entry["uuid"] == uuid
        assert entry["teksto"] == "getword"

    def test_list_entries(self, service):
        """Test listing entries."""
        # Create a few entries
        service.create({"teksto": "word1", "lingvo": "eo"})
        service.create({"teksto": "word2", "lingvo": "en"})

        entries = service.list()

        assert len(entries) >= 2

    def test_update_entry(self, service):
        """Test updating an entry."""
        data = {
            "teksto": "original",
            "lingvo": "eo",
        }

        created = service.create(data)
        uuid = created["uuid"]

        updated = service.update(uuid, {"teksto": "updated"})

        assert updated["teksto"] == "updated"

    def test_delete_hard(self, service):
        """Test hard delete."""
        data = {"teksto": "deleteword", "lingvo": "eo"}

        created = service.create(data)
        uuid = created["uuid"]

        service.delete(uuid, soft=False)

        entry = service.get(uuid)
        assert entry is None

    def test_count(self, service):
        """Test entry count using len(list())."""
        count_before = len(service.list())

        service.create({"teksto": "countword", "lingvo": "eo"})

        count_after = len(service.list())

        assert count_after == count_before + 1


class TestServiceFinds:
    """Test service find methods."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up test environment (isolation handled by conftest)."""
        yield

    @pytest.fixture
    def service(self):
        """Create service with test DB."""
        from A_vorto.service import get_service
        return get_service()

    def test_find_by_teksto(self, service):
        """Test finding by teksto (word text) via internal CRUDService."""
        data = {
            "teksto": "serchword",
            "lingvo": "eo",
        }

        service.create(data)

        entries = service.crud.search("teksto", "serchword")

        assert len(entries) >= 1
        assert entries[0]["teksto"] == "serchword"

    def test_find_by_lingvo(self, service):
        """Test finding by language via internal CRUDService."""
        data = {
            "teksto": "germanword",
            "lingvo": "de",
        }

        service.create(data)

        entry = service.crud.get_by_field("lingvo", "de")
        assert entry is not None
        assert entry["lingvo"] == "de"

    def test_find_by_uuid_prefix(self, service):
        """Test finding by UUID prefix."""
        data = {"teksto": "prefixword", "lingvo": "eo"}

        created = service.create(data)
        prefix = created["uuid"][:8]

        # Use list with filter or get directly
        entries = service.list()

        # Find matching prefix
        matching = [e for e in entries if e["uuid"].startswith(prefix)]
        assert len(matching) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])