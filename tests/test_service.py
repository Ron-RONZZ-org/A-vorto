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


class TestResolveLigiloRefs:
    """Tests for ligilo reference resolution in VortoService."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up test environment (isolation handled by conftest)."""
        yield

    @pytest.fixture
    def service(self):
        """Create service with test DB."""
        from A_vorto.service import get_service
        return get_service()

    def test_resolve_plain_uuid(self, service):
        """Plain UUID passes through."""
        entry_a = service.create({"teksto": "alpha", "lingvo": "eo"})
        uuid_a = entry_a["uuid"]
        result = service.resolve_ligilo_refs([uuid_a])
        assert result == [uuid_a]

    def test_resolve_short_uuid(self, service):
        """8-char UUID prefix resolves to full UUID."""
        entry_a = service.create({"teksto": "beta", "lingvo": "eo"})
        short = entry_a["uuid"][:8]
        result = service.resolve_ligilo_refs([short])
        assert result == [entry_a["uuid"]]

    def test_resolve_hash_prefix(self, service):
        """#-prefixed UUID strips # and resolves."""
        entry_a = service.create({"teksto": "gamma", "lingvo": "eo"})
        hash_ref = f"#{entry_a['uuid']}"
        result = service.resolve_ligilo_refs([hash_ref])
        assert result == [entry_a["uuid"]]

    def test_resolve_text_match(self, service):
        """Case-insensitive exact text resolves to UUID."""
        entry_a = service.create({"teksto": "Saluton", "lingvo": "eo"})
        result = service.resolve_ligilo_refs(["saluton"])
        assert result == [entry_a["uuid"]]

    def test_resolve_text_not_found(self, service):
        """Unmatched text produces empty result with warning."""
        result = service.resolve_ligilo_refs(["nonexistent"])
        assert result == []

    def test_resolve_mixed_refs(self, service):
        """Multiple ref types in one list all resolve."""
        entry_a = service.create({"teksto": "delta", "lingvo": "eo"})
        entry_b = service.create({"teksto": "epsilon", "lingvo": "eo"})
        result = service.resolve_ligilo_refs([
            entry_a["uuid"],
            "#" + entry_b["uuid"][:8],
        ])
        assert entry_a["uuid"] in result
        assert entry_b["uuid"] in result

    def test_resolve_vt_hash(self, service):
        """vt# prefix strips prefix and resolves UUID."""
        entry_a = service.create({"teksto": "zeta", "lingvo": "eo"})
        vt_ref = f"vt#{entry_a['uuid']}"
        result = service.resolve_ligilo_refs([vt_ref])
        assert result == [entry_a["uuid"]]

    def test_resolve_ec_hash_no_encik(self, service):
        """ec# ref without A-encik installed stored as-is."""
        result = service.resolve_ligilo_refs(["ec#4feb123f"])
        assert result == ["ec#4feb123f"]

    def test_create_with_text_ligilo(self, service):
        """create() resolves text ligilo refs automatically."""
        entry_a = service.create({"teksto": "source", "lingvo": "eo"})
        entry_b = service.create({"teksto": "target", "lingvo": "eo"})
        uuid_b = entry_b["uuid"]

        # Create source with text ref to target
        created = service.create({
            "teksto": "linked",
            "lingvo": "eo",
            "ligiloj": ["target"],
        })
        stored = service.get(created["uuid"])
        stored_ligiloj = stored.get("ligiloj") or []
        assert uuid_b in stored_ligiloj

    def test_find_by_teksto_exact(self, service):
        """find_by_teksto_exact matches case-insensitively."""
        service.create({"teksto": "ExActMatch", "lingvo": "eo"})
        entry = service.find_by_teksto_exact("exactmatch")
        assert entry is not None
        assert entry["teksto"] == "ExActMatch"

    def test_find_by_teksto_exact_not_found(self, service):
        """find_by_teksto_exact returns None for non-matching text."""
        entry = service.find_by_teksto_exact("nonexistent")
        assert entry is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])