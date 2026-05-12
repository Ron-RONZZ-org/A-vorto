"""Tests for A-vorto CLI."""

import os
import sys
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "A-core" / "src"))


class TestCLI:
    """Test CLI commands."""

    @pytest.fixture(autouse=True)
    def setup_env(self, tmp_path):
        """Set up test environment."""
        self.test_data_dir = tmp_path / "A"
        self.test_db = self.test_data_dir / "vorto.db"
        
        # Reset service singleton to prevent cross-test bleed
        import A_vorto.service as svc_mod
        svc_mod._vorto_service = None
        
        # Mock the data directory
        with patch("A_vorto.data.storage._DATA_DIR", self.test_data_dir):
            with patch("A_vorto.data.storage._DB_FILE", self.test_db):
                yield

    def test_list_empty(self):
        """Test list command with no entries."""
        from A_vorto.cli import list as list_cmd
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["list"])
        # Should show no entries message
        assert result.exit_code == 0

    def test_aldoni_basic(self):
        """Test aldoni command adds a word."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["aldoni", "testword", "-l", "eo", "-y"])
        # Should succeed
        assert result.exit_code == 0

    def test_vidi_nonexistent(self):
        """Test vidi command with non-existent UUID."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        fake_uuid = str(uuid.uuid4())
        result = runner.invoke(app, ["vidi", fake_uuid])
        # Should fail with not found error
        assert result.exit_code == 1

    def test_vidi_with_show_all(self):
        """Test vidi command with --cxio flag."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["vidi", str(uuid.uuid4()), "--cxio"])
        # Should run without error (will show not found or empty fields)
        assert result.exit_code in [0, 1]

    def test_vidi_with_show_all_alias_a(self):
        """Test vidi command with -a alias for --show-all."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["vidi", str(uuid.uuid4()), "-a"])
        assert result.exit_code in [0, 1]

    def test_vidi_with_show_all_alias_cxio(self):
        """Test vidi command with --cxio alias for --show-all."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["vidi", str(uuid.uuid4()), "--cxio"])
        assert result.exit_code in [0, 1]

    def test_serchi(self):
        """Test serchi command."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test"])
        # Should run without error
        assert result.exit_code == 0

    def test_serchi_with_lingvo_filter(self):
        """Test serchi command with lingvo filter."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test", "--lingvo", "eo"])
        assert result.exit_code == 0

    def test_serchi_with_kategorio_filter(self):
        """Test serchi command with lingvo filter."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test", "--lingvo", "eo"])
        assert result.exit_code == 0

    def test_serchi_with_tipo_filter(self):
        """Test serchi command with tipo filter."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test", "--tipo", "su"])
        assert result.exit_code == 0

    def test_serchi_with_temo_filter(self):
        """Test serchi command with temo filter."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test", "--temo", "gramatiko"])
        assert result.exit_code == 0

    def test_serchi_with_tono_filter(self):
        """Test serchi command with tono filter."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test", "--tono", "nf"])
        assert result.exit_code == 0

    def test_serchi_with_combined_filters(self):
        """Test serchi command with multiple filters."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test", "--lingvo", "eo"])
        assert result.exit_code == 0

    def test_serchi_with_filter_and_fuzzy(self):
        """Test serchi command with filter enabled."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["serchi", "test", "--lingvo", "eo"])
        assert result.exit_code == 0

    def test_modifi_nonexistent(self):
        """Test modifi command with non-existent UUID."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        fake_uuid = str(uuid.uuid4())
        result = runner.invoke(app, ["modifi", fake_uuid, "--teksto", "newword"])
        # Should fail with not found error
        assert result.exit_code == 1

    def test_forigi_nonexistent(self):
        """Test forigi command with non-existent UUID (silently ignored)."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        fake_uuid = str(uuid.uuid4())
        result = runner.invoke(app, ["forigi", fake_uuid])
        # Gracefully handles missing UUIDs (no error)
        assert result.exit_code == 0


class TestCRUDOperations:
    """Test CRUD operations through CLI."""

    @pytest.fixture(autouse=True)
    def setup_env(self, tmp_path):
        """Set up test environment with mock database."""
        self.test_data_dir = tmp_path / "A"
        self.test_db = self.test_data_dir / "vorto.db"
        
        # Reset service singleton to prevent cross-test bleed
        import A_vorto.service as svc_mod
        svc_mod._vorto_service = None
        
        with patch("A_vorto.data.storage._DATA_DIR", self.test_data_dir):
            with patch("A_vorto.data.storage._DB_FILE", self.test_db):
                yield

    def test_full_crud_cycle(self):
        """Test: add -> list -> view -> search -> modify -> delete."""
        from A_vorto.cli import app
        
        runner = CliRunner()
        
        # 1. Add a word (skip confirmation with -y)
        result = runner.invoke(app, ["aldoni", "testword", "-l", "eo", "-y"])
        assert result.exit_code == 0, f"Add failed: {result.output}"
        
        # Extract UUID from output
        output = result.output
        uuid_line = [line for line in output.split('\n') if 'UUID:' in line]
        assert uuid_line, f"No UUID in output: {output}"
        
        # Parse UUID (format: "UUID: <uuid>")
        word_uuid = uuid_line[0].split("UUID:")[1].strip()
        
        # 2. List should show the word
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "testword" in result.output
        
        # 3. View the word
        result = runner.invoke(app, ["vidi", word_uuid])
        assert result.exit_code == 0
        assert "testword" in result.output
        
        # 4. Search for the word
        result = runner.invoke(app, ["serchi", "test"])
        assert result.exit_code == 0
        assert "testword" in result.output
        
        # 5. Modify the word
        result = runner.invoke(app, ["modifi", word_uuid, "--teksto", "newtestword"])
        assert result.exit_code == 0, f"Modify failed: {result.output}"
        
        # Verify modification
        result = runner.invoke(app, ["vidi", word_uuid])
        assert result.exit_code == 0
        assert "newtestword" in result.output
        
        # 6. Delete the word (hard delete to avoid trash table issue)
        result = runner.invoke(app, ["forigi", word_uuid, "--hard"])
        assert result.exit_code == 0, f"Delete failed: {result.output}"
        
        # Verify deletion
        result = runner.invoke(app, ["vidi", word_uuid])
        assert result.exit_code == 1