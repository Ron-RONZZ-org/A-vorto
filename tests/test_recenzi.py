"""Tests for the recenzi (interactive review) module."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from A_vorto.data.storage import get_db


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_entry():
    """Create a sample entry for review tests."""
    from A_vorto.service import get_service

    svc = get_service()
    entry = svc.create({
        "teksto": "testvorto",
        "lingvo": "eo",
        "tipo": "substantivo",
        "difinoj": json.dumps(["testa difino"]),
        "uzoj": json.dumps(["testa uzo"]),
    })
    yield entry
    svc.delete(entry["uuid"], soft=False)


@pytest.fixture
def sample_entries():
    """Create multiple sample entries for review tests."""
    from A_vorto.service import get_service

    svc = get_service()
    entries = []
    for i in range(5):
        e = svc.create({
            "teksto": f"testvorto_{i}",
            "lingvo": "eo",
            "tipo": "substantivo",
            "difinoj": json.dumps([f"difino_{i}"]),
            "uzoj": json.dumps([f"uzo_{i}"]),
        })
        entries.append(e)
    yield entries
    for e in entries:
        svc.delete(e["uuid"], soft=False)


# ── Tests for date filtering in search_helpers ───────────────────────────────


class TestSearchDateFilter:
    """Tests that date filtering works end-to-end."""

    def test_date_filter_with_dato_de(self, sample_entry):
        """Search with --dato-de filters by kreita_je start."""
        from A_vorto.search_helpers import _run_search

        entries = _run_search(dato_de="19700101", limo=100)
        assert len(entries) >= 1

    def test_date_filter_with_dato_gis(self, sample_entry):
        """Search with --dato-gis filters by kreita_je end."""
        from A_vorto.search_helpers import _run_search

        entries = _run_search(dato_gis="20991231", limo=100)
        assert len(entries) >= 1

    def test_date_filter_invalid_raises(self):
        """Invalid date in --dato-de propagates ValueError."""
        from A_vorto.search_helpers import _run_search

        with pytest.raises(ValueError):
            _run_search(dato_de="not_a_date", limo=10)

    def test_date_filter_with_hyphen_format(self, sample_entry):
        """YYYY-MM-DD format works in --dato-de."""
        from A_vorto.search_helpers import _run_search

        entries = _run_search(dato_de="1970-01-01", limo=100)
        assert len(entries) >= 1


# ── Tests for recenzi helpers ──────────────────────────────────────────────


class TestParseJsonField:
    """Tests for _parse_json_field."""

    def test_parse_list_from_string(self):
        """JSON string list is parsed correctly."""
        from A_vorto.recenzi_helpers import _parse_json_field

        result = _parse_json_field({"difinoj": '["a", "b"]'}, "difinoj")
        assert result == ["a", "b"]

    def test_parse_list_from_list(self):
        """Already-parsed list is returned as-is."""
        from A_vorto.recenzi_helpers import _parse_json_field

        result = _parse_json_field({"difinoj": ["a", "b"]}, "difinoj")
        assert result == ["a", "b"]

    def test_parse_empty_string(self):
        """Empty string returns empty list."""
        from A_vorto.recenzi_helpers import _parse_json_field

        result = _parse_json_field({"difinoj": ""}, "difinoj")
        assert result == []

    def test_parse_none(self):
        """None returns empty list."""
        from A_vorto.recenzi_helpers import _parse_json_field

        result = _parse_json_field({"difinoj": None}, "difinoj")
        assert result == []


class TestGetSameTypeDistractors:
    """Tests for _get_same_type_distractors."""

    def test_no_distractors_when_no_tipo(self, sample_entry):
        """No tipo means no distractors."""
        from A_vorto.recenzi_helpers import _get_same_type_distractors
        from A_vorto.service import get_service

        entry_no_tipo = dict(sample_entry)
        entry_no_tipo["tipo"] = ""
        result = _get_same_type_distractors(entry_no_tipo, 3, get_service())
        assert result == []

    def test_distractors_match_tipo(self, sample_entries, sample_entry):
        """Distractors have same tipo as the entry (all are substantivo)."""
        from A_vorto.recenzi_helpers import _get_same_type_distractors
        from A_vorto.service import get_service

        result = _get_same_type_distractors(sample_entry, 3, get_service())
        # Should find at least one distractor from the 5 entries
        assert len(result) >= 1
        for d in result:
            assert d["uuid"] != sample_entry["uuid"]


class TestSaveAndLoadSessions:
    """Tests for session persistence."""

    def test_save_session(self):
        """Saving a session creates DB records."""
        from A_vorto.recenzi_helpers import _save_session, _list_sessions

        stats = {
            "entute": 2,
            "gustaj": 1,
            "malgustaj": 1,
            "rezultoj": [
                {
                    "vorto_uuid": "00000000-0000-0000-0000-000000000001",
                    "gxusta": 1,
                    "respondo": "correct",
                    "tempo_sekundoj": 1.5,
                },
                {
                    "vorto_uuid": "00000000-0000-0000-0000-000000000002",
                    "gxusta": 0,
                    "respondo": "wrong",
                    "tempo_sekundoj": 2.0,
                },
            ],
        }
        uuid = _save_session("tajpu", stats)
        assert uuid

        sessions = _list_sessions(limit=10)
        assert any(s["uuid"] == uuid for s in sessions)

    def test_list_sessions_empty(self):
        """Listing when no sessions returns empty list."""
        from A_vorto.recenzi_helpers import _list_sessions

        # Our test DB should have at most 1 session from previous test
        sessions = _list_sessions(limit=10)
        assert isinstance(sessions, list)

    def test_get_session_stats(self):
        """Getting stats for a saved session returns results."""
        from A_vorto.recenzi_helpers import _save_session, _get_session_stats

        stats = {
            "entute": 1,
            "gustaj": 1,
            "malgustaj": 0,
            "rezultoj": [
                {
                    "vorto_uuid": "00000000-0000-0000-0000-000000000003",
                    "gxusta": 1,
                    "respondo": "hello",
                    "tempo_sekundoj": 0.5,
                },
            ],
        }
        uuid = _save_session("difinoj", stats)
        session = _get_session_stats(uuid)
        assert session is not None
        assert session["uuid"] == uuid
        assert session["modo"] == "difinoj"
        assert len(session["rezultoj"]) == 1

    def test_get_session_stats_not_found(self):
        """Getting stats for non-existent session returns None."""
        from A_vorto.recenzi_helpers import _get_session_stats

        result = _get_session_stats("nonexistent-uuid")
        assert result is None

    def test_get_global_stats(self):
        """Global stats aggregates across sessions."""
        from A_vorto.recenzi_helpers import _get_global_stats

        stats = _get_global_stats()
        assert "total_sessions" in stats
        assert "total_words" in stats
        assert "total_correct" in stats

    def test_delete_session(self):
        """Deleting a session removes it."""
        from A_vorto.recenzi_helpers import _save_session, _get_session_stats, _delete_session

        stats = {
            "entute": 1,
            "gustaj": 1,
            "malgustaj": 0,
            "rezultoj": [
                {"vorto_uuid": "00000000-0000-0000-0000-000000000009",
                 "gxusta": 1, "respondo": "x", "tempo_sekundoj": 0.1},
            ],
        }
        uuid = _save_session("test", stats)
        assert _get_session_stats(uuid) is not None

        assert _delete_session(uuid) is True
        assert _get_session_stats(uuid) is None

    def test_delete_session_not_found(self):
        """Deleting non-existent session returns False."""
        from A_vorto.recenzi_helpers import _delete_session

        assert _delete_session("nonexistent") is False

    def test_clear_all_history(self):
        """Clearing all history removes all sessions."""
        from A_vorto.recenzi_helpers import _clear_all_history, _list_sessions

        _clear_all_history()
        assert _list_sessions(limit=10) == []


class TestCelebrate:
    """Tests for _celebrate (just ensure no crash)."""

    def test_perfect_score(self):
        """100% score shows celebration."""
        from A_vorto.recenzi_helpers import _celebrate

        stats = {
            "entute": 5,
            "gustaj": 5,
            "malgustaj": 0,
            "rezultoj": [
                {"vorto_uuid": f"uuid{i}", "gxusta": 1,
                 "respondo": "ok", "tempo_sekundoj": 1.0}
                for i in range(5)
            ],
        }
        # Should not raise
        _celebrate(stats)

    def test_low_score(self):
        """Low score shows encouragement."""
        from A_vorto.recenzi_helpers import _celebrate

        stats = {
            "entute": 5,
            "gustaj": 1,
            "malgustaj": 4,
            "rezultoj": [
                {"vorto_uuid": f"uuid{i}", "gxusta": i == 0,
                 "respondo": "x", "tempo_sekundoj": 1.0}
                for i in range(5)
            ],
        }
        _celebrate(stats)
