"""Test isolation for A-vorto — prevents writes to real database."""

from __future__ import annotations
import os

import pytest


@pytest.fixture(autouse=True)
def isolate_vorto(monkeypatch, tmp_path):
    """Isolate database to tmp_path to prevent real data pollution.

    Resets all module-level singletons so each test gets a fresh DB
    connection and service instance, even when tests are run in any order.

    Also sets A_DIR to redirect ALL A-core paths (including A.core.links
    LinksDB which uses data_dir() from A.core.paths) to tmp_path.
    """
    import A_vorto.data.storage as storage_module
    import A_vorto.service as service_module

    # Redirect ALL A-core paths via A_DIR env var (covers LinksDB too)
    monkeypatch.setenv("A_DIR", str(tmp_path))

    # Reset singletons before patching paths
    monkeypatch.setattr(storage_module, "_db_instance", None)
    monkeypatch.setattr(service_module, "_vorto_service", None)

    # Redirect A-vorto storage paths (matching ~/.local/share/A/)
    data_dir_val = tmp_path / "data"
    monkeypatch.setattr(storage_module, "_DATA_DIR", data_dir_val)
    monkeypatch.setattr(storage_module, "_DB_FILE", data_dir_val / "vorto.db")
