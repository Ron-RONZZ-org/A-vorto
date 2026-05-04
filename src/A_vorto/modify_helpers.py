"""Helpers for aldoni and modifi commands."""

from __future__ import annotations

from typing import Any, Optional

from A import error, info, tr_multi
from A.utils import copy_to_clipboard
from A.utils.output import console

from A_vorto.service import get_service


def _find_duplicate(teksto: str) -> dict[str, Any] | None:
    """Check if an entry with the same teksto already exists.

    Performs case-insensitive exact match (not prefix).
    Returns the existing entry dict if found, None otherwise.

    Args:
        teksto: The word text to check.

    Returns:
        Existing entry dict or None.
    """
    service = get_service()
    from A_vorto.data.storage import get_db
    db = get_db()
    row = db.execute_one(
        "SELECT * FROM vorto WHERE LOWER(teksto) = ? AND forigita_je IS NULL",
        (teksto.lower(),),
    )
    return dict(row) if row else None


def _build_create_data(
    teksto: str,
    lingvo: str | None = None,
    kategorio: str | None = None,
    tipo: str | None = None,
    temo: str | None = None,
    tono: str | None = None,
    nivelo: float | None = None,
    difinoj: list[str] | None = None,
    uzoj: list[str] | None = None,
    etikedoj: list[str] | None = None,
    ligiloj: list[str] | None = None,
    autoro: str | None = None,
    verko: str | None = None,
) -> dict[str, Any]:
    """Build data dict for aldoni (create) command.

    Args:
        teksto: Word text.
        lingvo: Language code.
        kategorio: Category (auto-detected if None).
        tipo: Type abbreviation(s).
        temo: Theme.
        tono: Tonality.
        nivelo: Proficiency level.
        difinoj: Definition strings (may include paired usage).
        uzoj: Standalone usage examples.
        etikedoj: Tags in key:value format.
        ligiloj: Link UUIDs.
        autoro: Author.
        verko: Work/source.

    Returns:
        Data dict ready for service.create().
    """
    from A_vorto.utils import (
        detect_kategorio,
        normalize_tipo,
        normalize_tono,
        parse_etikedoj,
        split_difino_uzo,
    )

    effective_kategorio = kategorio or detect_kategorio(teksto)
    effective_tipo = normalize_tipo(tipo)
    effective_tono = normalize_tono(tono)

    data: dict[str, object] = {
        "teksto": teksto,
        "kategorio": effective_kategorio,
    }
    if lingvo:
        data["lingvo"] = lingvo
    if effective_tipo is not None:
        data["tipo"] = ",".join(effective_tipo)
    if temo:
        data["temo"] = temo
    if effective_tono is not None:
        data["tono"] = effective_tono
    if autoro:
        data["autoro"] = autoro
    if verko:
        data["verko"] = verko
    if nivelo is not None:
        data["nivelo"] = nivelo

    # Process difinoj with optional paired uzoj
    parsed_difinoj: list[str] = []
    parsed_uzoj: list[str] = []
    if difinoj:
        for raw in difinoj:
            d, u = split_difino_uzo(raw)
            parsed_difinoj.append(d)
            parsed_uzoj.append(u)
        data["difinoj"] = parsed_difinoj
        data["uzoj"] = parsed_uzoj

    # Standalone usage examples (appended after paired uzoj)
    if uzoj:
        existing = data.get("uzoj", [])
        if isinstance(existing, list):
            data["uzoj"] = existing + list(uzoj)

    # Parse etikedoj
    if etikedoj:
        data["etikedoj"] = parse_etikedoj(etikedoj)

    # Add ligiloj
    if ligiloj:
        data["ligiloj"] = list(ligiloj)

    return data


def _build_update_data(
    existing: dict[str, Any],
    teksto: str | None = None,
    lingvo: str | None = None,
    kategorio: str | None = None,
    tipo: str | None = None,
    temo: str | None = None,
    tono: str | None = None,
    nivelo: float | None = None,
    difinoj: list[str] | None = None,
    uzoj: list[str] | None = None,
    etikedoj: list[str] | None = None,
    autoro: str | None = None,
    verko: str | None = None,
    clear_difinoj: bool = False,
    clear_uzoj: bool = False,
    clear_etikedoj: bool = False,
    clear_ligiloj: bool = False,
    clear_tipo: bool = False,
    ligilo_add: list[str] | None = None,
    ligilo_remove: list[str] | None = None,
) -> dict[str, Any]:
    """Build update data dict for modifi command.

    Args:
        existing: Existing entry dict.
        Same as modifi CLI command parameters.

    Returns:
        Data dict ready for service.update(), or empty dict if no changes.
    """
    from A_vorto.utils import normalize_tipo, normalize_tono, parse_etikedoj, split_difino_uzo

    data: dict[str, object] = {}
    if teksto is not None:
        data["teksto"] = teksto
    if lingvo is not None:
        data["lingvo"] = lingvo
    if kategorio is not None:
        data["kategorio"] = kategorio
    if temo is not None:
        data["temo"] = temo
    if autoro is not None:
        data["autoro"] = autoro
    if verko is not None:
        data["verko"] = verko
    if nivelo is not None:
        data["nivelo"] = nivelo

    # tipo: normalize if provided, clear if flag set
    if tipo is not None:
        effective = normalize_tipo(tipo)
        if effective is not None:
            data["tipo"] = ",".join(effective)
    if clear_tipo:
        data["tipo"] = None

    # tono: normalize if provided
    if tono is not None:
        effective = normalize_tono(tono)
        if effective is not None:
            data["tono"] = effective

    # difinoj/uzoj
    if clear_difinoj:
        data["difinoj"] = []
        data["uzoj"] = []
    elif difinoj is not None:
        parsed_difinoj: list[str] = []
        parsed_uzoj: list[str] = []
        for raw in difinoj:
            d, u = split_difino_uzo(raw)
            parsed_difinoj.append(d)
            parsed_uzoj.append(u)
        data["difinoj"] = parsed_difinoj
        data["uzoj"] = parsed_uzoj

    if clear_uzoj:
        data["uzoj"] = []
    elif uzoj is not None:
        existing_uzoj = existing.get("uzoj") or []
        if isinstance(existing_uzoj, list):
            data["uzoj"] = existing_uzoj + list(uzoj)
        else:
            data["uzoj"] = list(uzoj)

    # etikedoj
    if clear_etikedoj:
        data["etikedoj"] = {}
    elif etikedoj is not None:
        data["etikedoj"] = parse_etikedoj(etikedoj)

    # ligiloj: clear, add, or remove
    if clear_ligiloj:
        data["ligiloj"] = []
    elif ligilo_add is not None or ligilo_remove is not None:
        existing_ligiloj = set(existing.get("ligiloj") or [])
        if ligilo_add:
            existing_ligiloj.update(ligilo_add)
        if ligilo_remove:
            existing_ligiloj.difference_update(ligilo_remove)
        data["ligiloj"] = list(existing_ligiloj)

    return data


def _handle_create_result(entry: dict[str, Any], teksto: str, kopii: bool, semantika_kopii: bool) -> None:
    """Handle result of aldoni command.

    Args:
        entry: Created entry dict.
        teksto: Word text for display.
        kopii: Copy #uuid to clipboard.
        semantika_kopii: Copy [teksto](#uuid) to clipboard.
    """
    info(tr_multi(f"Aldonis {teksto}", f"Added {teksto}", f"Ajoute {teksto}"))
    console.print(f"[green]UUID:[/] {entry.get('uuid')}")

    if kopii or semantika_kopii:
        if kopii:
            copy_to_clipboard(f"#{entry['uuid'][:8]}")
        if semantika_kopii:
            copy_to_clipboard(f"[{entry['teksto']}](#{entry['uuid'][:8]})")


__all__ = ["_build_create_data", "_build_update_data", "_handle_create_result"]