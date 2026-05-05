"""Test isolation for A-vorto — prevents writes to real database."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def isolate_vorto(monkeypatch, tmp_path):
    """Isolate database to tmp_path to prevent real data pollution.

    A-vorto writes to _DATA_DIR / "vorto.db". We override both module-level
    path variables before any test imports them.
    """
    import A_vorto.data.storage as storage_module

    monkeypatch.setattr(storage_module, "_DATA_DIR", tmp_path)
    monkeypatch.setattr(storage_module, "_DB_FILE", tmp_path / "vorto.db")
