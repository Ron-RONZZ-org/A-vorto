"""Utility functions for A-vorto — type normalization, text parsing."""

from __future__ import annotations

import re
from typing import Any

# ──────────────────────────────────────────────────────────────────────────────
# Type normalization maps  (Esperanto grammatical abbreviations → full names)
# ──────────────────────────────────────────────────────────────────────────────

TIPO_MAP: dict[str, str] = {
    # Word subtypes
    "su": "substantivo",
    "substantivo": "substantivo",
    "sn": "substantivo-neutra",
    "substantivo-neutra": "substantivo-neutra",
    "sp": "substantivo-plurala",
    "substantivo-plurala": "substantivo-plurala",
    "sip": "substantivo-ina-plurala",
    "substantivo-ina-plurala": "substantivo-ina-plurala",
    "svp": "substantivo-vira-plurala",
    "substantivo-vira-plurala": "substantivo-vira-plurala",
    "sui": "substantivo-ina",
    "si": "substantivo-ina",
    "suf": "substantivo-ina",
    "substantivo-ina": "substantivo-ina",
    "suv": "substantivo-vira",
    "sv": "substantivo-vira",
    "sum": "substantivo-vira",
    "substantivo-vira": "substantivo-vira",
    "ve": "verbo",
    "verbo": "verbo",
    "vt": "verbo-transitiva",
    "transitiva": "verbo-transitiva",
    "verbo-transitiva": "verbo-transitiva",
    "vnt": "verbo-nerekta-transitiva",
    "nerekta-transitiva": "verbo-nerekta-transitiva",
    "verbo-nerekta-transitiva": "verbo-nerekta-transitiva",
    "vn": "verbo-netransitiva",
    "netransitiva": "verbo-netransitiva",
    "verbo-netransitiva": "verbo-netransitiva",
    "vr": "refleksiva-verbo",
    "refleksiva-verbo": "refleksiva-verbo",
    "aj": "adjektivo",
    "adjektivo": "adjektivo",
    "av": "adverbo",
    "adverbo": "adverbo",
    # Phrase subtypes
    "pa": "parola",
    "parola": "parola",
    "sk": "skriba",
    "skriba": "skriba",
    # Sentence subtypes
    "ci": "citajxo",
    "citajxo": "citajxo",
    "sxe": "sxerco",
    "sxerco": "sxerco",
    "pr": "proverbo",
    "proverbo": "proverbo",
    "po": "poemo",
    "poemo": "poemo",
    "ek": "ekzemplo",
    "ekzemplo": "ekzemplo",
    # Common abbreviations
    "subst": "substantivo",
    "adj": "adjektivo",
    "verb": "verbo",
    "adv": "adverbo",
    "konj": "konjunkcio",
    "konjunkcio": "konjunkcio",
    "prep": "prepozicio",
    "prepozicio": "prepozicio",
    "inter": "interjekcio",
    "interjekcio": "interjekcio",
    "subs": "substantivo",
    "subs.": "substantivo",
}

TONO_MAP: dict[str, str] = {
    "nf": "neformala",
    "neformala": "neformala",
    "in": "neformala",
    "informala": "neformala",
    "fo": "formala",
    "formala": "formala",
    "am": "ambaux",
    "ambaux": "ambaux",
    "f": "fakula",
    "fakula": "fakula",
    "p": "poezia",
    "poezia": "poezia",
    "m": "meznombra",
    "meznombra": "meznombra",
    "sf": "sciencafakula",
    "sciencafakula": "sciencafakula",
    "sp": "sciencapoezia",
    "sciencapoezia": "sciencapoezia",
}


# ──────────────────────────────────────────────────────────────────────────────
# Type normalization
# ──────────────────────────────────────────────────────────────────────────────


def normalize_tipo(tipo: str | None) -> list[str] | None:
    """Normalize a comma/semicolon-separated tipo string into a list.

    Each abbreviation is mapped via TIPO_MAP. Unknown values are passed
    through as-is. Duplicates are removed preserving first-occurrence order.

    Args:
        tipo: Comma or semicolon-separated abbreviations (e.g. "su,aj" or "vt;aj").

    Returns:
        Normalized list of tipo strings, or None if input is empty/None.
    """
    if not tipo:
        return None
    parts = [p.strip() for p in re.split(r"[,;]", str(tipo)) if p.strip()]
    if not parts:
        return None
    normalized: list[str] = []
    seen: set[str] = set()
    for part in parts:
        norm = TIPO_MAP.get(part.lower(), part)
        if norm not in seen:
            seen.add(norm)
            normalized.append(norm)
    return normalized if normalized else None


def normalize_tono(tono: str | None) -> str | None:
    """Normalize a tono abbreviation via TONO_MAP.

    Args:
        tono: Abbreviation (e.g. "nf", "fo").

    Returns:
        Normalized tono string, or None if input is empty/None.
        Unknown abbreviations are passed through unchanged.
    """
    if not tono:
        return None
    return TONO_MAP.get(tono.lower(), tono)


# ──────────────────────────────────────────────────────────────────────────────
# Text normalization
# ──────────────────────────────────────────────────────────────────────────────


def normalize_multiline_text(text: str) -> str:
    """Convert escaped/newline markers into actual multiline text.

    Handles:
    - ``<br>`` / ``<br/>`` / ``<br />`` → newline
    - ``\\r\\n``, ``\\n``, ``\\r`` → actual newlines

    Args:
        text: Raw text possibly containing escape markers.

    Returns:
        Cleaned text with actual newlines.
    """
    normalized = str(text or "")
    normalized = re.sub(r"(?i)<br\s*/?>", "\n", normalized)
    normalized = normalized.replace("\\r\\n", "\n")
    normalized = normalized.replace("\\n", "\n")
    normalized = normalized.replace("\\r", "\n")
    return normalized.strip()


def split_difino_uzo(raw: str) -> tuple[str, str]:
    """Split a combined definition+usage string into separate parts.

    Supported syntaxes:
    - ``difino::uzo`` (preferred — shell-safe, same keystrokes as ``:{...}``)
    - ``difino : uzo`` (natural language — space-colon-space)
    - ``difino:{uzo}`` (colon-braced — also valid)
    - ``difino:*uzo*`` (legacy)

    Args:
        raw: Combined string.

    Returns:
        Tuple of (difino, uzo). Usage may be empty string if not present.
    """
    text = normalize_multiline_text(raw)
    # Shell-safe: difino::uzo
    if "::" in text:
        left, right = text.split("::", 1)
        return left.strip(), right.strip()
    # Natural language: difino : uzo  (space-colon-space)
    if " : " in text:
        left, right = text.split(" : ", 1)
        return left.strip(), right.strip()
    # Preferred: difino:{uzo}
    m_braced = re.match(r"^(.*?):\{(.+)\}$", text)
    if m_braced:
        return m_braced.group(1).strip(), m_braced.group(2).strip()
    # Legacy: difino:*uzo*
    m = re.match(r"^(.*?):\*(.+)\*$", text)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # No usage part
    return text, ""


def detect_kategorio(teksto: str) -> str:
    """Auto-detect entry category from the word text.

    Rules:
    - Single word → ``vorto``
    - Multiple words, no sentence-ending punctuation → ``frazo``
    - Multiple words with punctuation → ``frazdaro``

    Args:
        teksto: The word text to analyze.

    Returns:
        ``"vorto"``, ``"frazo"``, or ``"frazdaro"``.
    """
    words = teksto.strip().split()
    if not words or len(words) == 1:
        return "vorto"
    if re.search(r"[.?!;\u2026]", teksto):
        return "frazdaro"
    return "frazo"


def parse_etikedoj(items: list[str] | None) -> dict[str, str]:
    """Parse a list of ``KEY:VALUE`` strings into a dictionary.

    Args:
        items: List of strings in ``key:value`` format, or None.

    Returns:
        Dictionary of key-value pairs. Empty dict if input is None or empty.
    """
    if not items:
        return {}
    result: dict[str, str] = {}
    for item in items:
        k, _, v = item.partition(":")
        result[k.strip()] = v.strip()
    return result


__all__ = [
    "TIPO_MAP",
    "TONO_MAP",
    "normalize_tipo",
    "normalize_tono",
    "normalize_multiline_text",
    "split_difino_uzo",
    "detect_kategorio",
    "parse_etikedoj",
]
