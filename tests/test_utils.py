"""Tests for A-vorto utility functions."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from A_vorto.utils import (
    TIPO_MAP,
    TONO_MAP,
    normalize_tipo,
    normalize_tono,
    normalize_multiline_text,
    split_difino_uzo,
    detect_kategorio,
    parse_etikedoj,
)


# ──────────────────────────────────────────────────────────────────────────────
# TIPO_MAP integrity
# ──────────────────────────────────────────────────────────────────────────────


class TestTipoMap:
    """Verify TIPO_MAP consistency."""

    def test_all_keys_map_to_non_empty(self):
        """Every key in TIPO_MAP maps to a non-empty string."""
        for key, value in TIPO_MAP.items():
            assert value, f"Key {key!r} maps to empty value"

    def test_self_mapping_stable(self):
        """Full names map to themselves (idempotent)."""
        full_names = {
            "substantivo",
            "substantivo-neutra",
            "substantivo-plurala",
            "substantivo-ina-plurala",
            "substantivo-vira-plurala",
            "substantivo-ina",
            "substantivo-vira",
            "verbo",
            "verbo-transitiva",
            "verbo-nerekta-transitiva",
            "verbo-netransitiva",
            "refleksiva-verbo",
            "adjektivo",
            "adverbo",
            "parola",
            "skriba",
            "citajxo",
            "sxerco",
            "proverbo",
            "poemo",
            "ekzemplo",
            "konjunkcio",
            "prepozicio",
            "interjekcio",
        }
        for name in full_names:
            assert TIPO_MAP[name] == name, f"{name!r} should map to itself"

    def test_common_abbreviations(self):
        """Known abbreviations map correctly."""
        cases = {
            "su": "substantivo",
            "aj": "adjektivo",
            "vt": "verbo-transitiva",
            "ve": "verbo",
            "av": "adverbo",
            "subst": "substantivo",
            "adj": "adjektivo",
            "konj": "konjunkcio",
            "prep": "prepozicio",
        }
        for abbr, expected in cases.items():
            assert TIPO_MAP[abbr] == expected


class TestTonoMap:
    """Verify TONO_MAP consistency."""

    def test_all_keys_map_to_non_empty(self):
        """Every key in TONO_MAP maps to a non-empty string."""
        for key, value in TONO_MAP.items():
            assert value, f"Key {key!r} maps to empty value"

    def test_self_mapping_stable(self):
        """Full names map to themselves."""
        for name in ("neformala", "formala", "ambaux", "fakula", "poezia", "meznombra"):
            assert TONO_MAP[name] == name

    def test_common_abbreviations(self):
        """Known abbreviations map correctly."""
        cases = {
            "nf": "neformala",
            "fo": "formala",
            "am": "ambaux",
            "f": "fakula",
            "p": "poezia",
        }
        for abbr, expected in cases.items():
            assert TONO_MAP[abbr] == expected


# ──────────────────────────────────────────────────────────────────────────────
# normalize_tipo
# ──────────────────────────────────────────────────────────────────────────────


class TestNormalizeTipo:
    """Tests for normalize_tipo()."""

    def test_comma_separated(self):
        """Comma-separated abbreviations are normalized."""
        result = normalize_tipo("su,aj")
        assert result == ["substantivo", "adjektivo"]

    def test_semicolon_separated(self):
        """Semicolon-separated abbreviations are supported."""
        result = normalize_tipo("vt;aj")
        assert result == ["verbo-transitiva", "adjektivo"]

    def test_mixed_separator(self):
        """Mixed comma and semicolon."""
        result = normalize_tipo("su,vt;aj")
        assert "substantivo" in result
        assert "verbo-transitiva" in result
        assert "adjektivo" in result

    def test_deduplicates(self):
        """Duplicates are removed (first occurrence wins)."""
        result = normalize_tipo("su,substantivo")
        assert result == ["substantivo"]

    def test_deduplicates_across_abbreviation_and_full(self):
        """Same tipo via abbreviation and full name deduplicates."""
        result = normalize_tipo("substantivo,su")
        assert result == ["substantivo"]

    def test_unknown_passed_through(self):
        """Unknown abbreviations are passed through unchanged."""
        result = normalize_tipo("su,foo_bar")
        assert result == ["substantivo", "foo_bar"]

    def test_none_returns_none(self):
        """None input returns None."""
        assert normalize_tipo(None) is None

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        assert normalize_tipo("") is None

    def test_single_abbreviation(self):
        """Single abbreviation works."""
        result = normalize_tipo("vt")
        assert result == ["verbo-transitiva"]

    def test_case_insensitive(self):
        """Input is case-insensitive."""
        result = normalize_tipo("SU,Aj")
        assert result == ["substantivo", "adjektivo"]


# ──────────────────────────────────────────────────────────────────────────────
# normalize_tono
# ──────────────────────────────────────────────────────────────────────────────


class TestNormalizeTono:
    """Tests for normalize_tono()."""

    def test_known_abbreviation(self):
        """Known tono abbreviation is normalized."""
        assert normalize_tono("nf") == "neformala"

    def test_unknown_passed_through(self):
        """Unknown tono is passed through."""
        assert normalize_tono("unknown") == "unknown"

    def test_none_returns_none(self):
        """None input returns None."""
        assert normalize_tono(None) is None

    def test_empty_string_returns_none(self):
        """Empty string returns None."""
        assert normalize_tono("") is None

    def test_full_name_preserved(self):
        """Full name maps to itself."""
        assert normalize_tono("neformala") == "neformala"

    def test_case_insensitive(self):
        """Input is case-insensitive."""
        assert normalize_tono("NF") == "neformala"

    def test_legacy_alias(self):
        """Legacy aliases work."""
        assert normalize_tono("in") == "neformala"
        assert normalize_tono("informala") == "neformala"


# ──────────────────────────────────────────────────────────────────────────────
# normalize_multiline_text
# ──────────────────────────────────────────────────────────────────────────────


class TestNormalizeMultilineText:
    """Tests for normalize_multiline_text()."""

    def test_br_to_newline(self):
        """<br> tags become newlines."""
        assert normalize_multiline_text("a<br>b") == "a\nb"

    def test_br_with_slash(self):
        """<br/> becomes newline."""
        assert normalize_multiline_text("a<br/>b") == "a\nb"

    def test_br_with_space(self):
        """<br /> becomes newline."""
        assert normalize_multiline_text("a<br />b") == "a\nb"

    def test_escaped_newline(self):
        r"""Escaped \n becomes newline."""
        assert normalize_multiline_text("a\\nb") == "a\nb"

    def test_escaped_crlf(self):
        r"""Escaped \r\n becomes newline."""
        assert normalize_multiline_text("a\\r\\nb") == "a\nb"

    def test_escaped_cr(self):
        r"""Escaped \r becomes newline."""
        assert normalize_multiline_text("a\\rb") == "a\nb"

    def test_strips_whitespace(self):
        """Result is stripped."""
        result = normalize_multiline_text("  hello  ")
        assert result == "hello"

    def test_empty_string(self):
        """Empty string returns empty."""
        assert normalize_multiline_text("") == ""

    def test_no_markers(self):
        """Text without markers is unchanged (except strip)."""
        assert normalize_multiline_text("hello world") == "hello world"


# ──────────────────────────────────────────────────────────────────────────────
# split_difino_uzo
# ──────────────────────────────────────────────────────────────────────────────


class TestSplitDifinoUzo:
    """Tests for split_difino_uzo()."""

    def test_braced_syntax(self):
        """difino:{uzo} syntax."""
        d, u = split_difino_uzo("dif:{uzo}")
        assert d == "dif"
        assert u == "uzo"

    def test_shell_safe_syntax(self):
        """difino::uzo syntax (shell-safe)."""
        d, u = split_difino_uzo("dif::uzo")
        assert d == "dif"
        assert u == "uzo"

    def test_legacy_syntax(self):
        """difino:*uzo* syntax (legacy)."""
        d, u = split_difino_uzo("dif:*uzo*")
        assert d == "dif"
        assert u == "uzo"

    def test_no_uzo(self):
        """No usage part returns empty string."""
        d, u = split_difino_uzo("dif")
        assert d == "dif"
        assert u == ""

    def test_difino_with_colon_no_uzo(self):
        """String with single colon but no uzo markers."""
        d, u = split_difino_uzo("just: text")
        assert d == "just: text"
        assert u == ""

    def test_multiline_normalized(self):
        """Multiline escapes are normalized before parsing."""
        d, u = split_difino_uzo("line1\\nline2::uzo")
        assert d == "line1\nline2"
        assert u == "uzo"

    def test_empty_string(self):
        """Empty string returns empty difino."""
        d, u = split_difino_uzo("")
        assert d == ""
        assert u == ""

    # ── Single colon with surrounding spaces ( : ) ────────────────────────

    def test_single_colon_with_spaces(self):
        """Space-colon-space splits correctly."""
        d, u = split_difino_uzo("def : uzo")
        assert d == "def"
        assert u == "uzo"

    def test_single_colon_no_leading_space(self):
        """Colon with space only after does NOT split."""
        d, u = split_difino_uzo("def: uzo")
        assert d == "def: uzo"
        assert u == ""

    def test_single_colon_multiword(self):
        """Multi-word natural language example with space-colon-space."""
        d, u = split_difino_uzo("aspect general : une ruine d'allure")
        assert d == "aspect general"
        assert u == "une ruine d'allure"

    def test_single_colon_trailing_only(self):
        """Nothing after colon: normalize strips trailing space, no split."""
        d, u = split_difino_uzo("def : ")
        assert d == "def :"
        assert u == ""

    def test_double_colon_still_takes_priority(self):
        """Explicit :: takes priority when both :: and  :  are present."""
        d, u = split_difino_uzo("def : uzo :: extra")
        assert d == "def : uzo"
        assert u == "extra"


# ──────────────────────────────────────────────────────────────────────────────
# detect_kategorio
# ──────────────────────────────────────────────────────────────────────────────


class TestDetectKategorio:
    """Tests for detect_kategorio()."""

    def test_single_word_is_vorto(self):
        """Single word returns 'vorto'."""
        assert detect_kategorio("casa") == "vorto"

    def test_two_words_is_frazo(self):
        """Two words without punctuation returns 'frazo'."""
        assert detect_kategorio("ciao mondo") == "frazo"

    def test_three_words_is_frazo(self):
        """Three words without punctuation returns 'frazo'."""
        assert detect_kategorio("ciao a tutti") == "frazo"

    def test_with_period_is_frazdaro(self):
        """Words with period returns 'frazdaro'."""
        assert detect_kategorio("Ciao mondo.") == "frazdaro"

    def test_with_exclamation_is_frazdaro(self):
        """Words with exclamation returns 'frazdaro'."""
        assert detect_kategorio("Ciao mondo!") == "frazdaro"

    def test_with_question_is_frazdaro(self):
        """Words with question mark returns 'frazdaro'."""
        assert detect_kategorio("Ciao mondo?") == "frazdaro"

    def test_with_ellipsis(self):
        """Words with ellipsis returns 'frazdaro'."""
        assert detect_kategorio("Ciao mondo\u2026") == "frazdaro"

    def test_with_semicolon_is_frazdaro(self):
        """Words with semicolon returns 'frazdaro'."""
        assert detect_kategorio("Ciao; mondo") == "frazdaro"

    def test_empty_string_is_vorto(self):
        """Empty string returns 'vorto'."""
        assert detect_kategorio("") == "vorto"


# ──────────────────────────────────────────────────────────────────────────────
# parse_etikedoj
# ──────────────────────────────────────────────────────────────────────────────


class TestParseEtikedoj:
    """Tests for parse_etikedoj()."""

    def test_single_pair(self):
        """Single KEY:VALUE pair."""
        result = parse_etikedoj(["lang:fr"])
        assert result == {"lang": "fr"}

    def test_multiple_pairs(self):
        """Multiple KEY:VALUE pairs."""
        result = parse_etikedoj(["lang:fr", "register:formal"])
        assert result == {"lang": "fr", "register": "formal"}

    def test_value_with_spaces(self):
        """Value after colon can have spaces."""
        result = parse_etikedoj(["note: important word"])
        assert result == {"note": "important word"}

    def test_key_with_spaces(self):
        """Key before colon can have spaces (though unusual)."""
        result = parse_etikedoj(["my key: value"])
        assert result == {"my key": "value"}

    def test_none_returns_empty(self):
        """None input returns empty dict."""
        assert parse_etikedoj(None) == {}

    def test_empty_list_returns_empty(self):
        """Empty list returns empty dict."""
        assert parse_etikedoj([]) == {}

    def test_colon_in_value(self):
        """Value containing colon is preserved (only first colon splits)."""
        result = parse_etikedoj(["time:10:30"])
        assert result == {"time": "10:30"}

    def test_no_colon_returns_full_string_as_key(self):
        """If no colon, the entire string is the key with empty value."""
        result = parse_etikedoj(["justkey"])
        assert result == {"justkey": ""}
