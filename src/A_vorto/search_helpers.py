"""Search helpers for serci command with interactive selection."""

from __future__ import annotations

from typing import Any

from A import info, tr_multi
from A.utils.date import date_range
from A.utils.output import console, print_table
from A.utils.interactive import select_candidate

from A_vorto.service import get_service


def _run_search(
    teksto: str | None = None,
    ligilo: str | None = None,
    lingvo: str | None = None,
    tipo: str | None = None,
    temo: str | None = None,
    tono: str | None = None,
    autoro: str | None = None,
    verko: str | None = None,
    nivelo_min: float | None = None,
    nivelo_max: float | None = None,
    dato_de: str | None = None,
    dato_gis: str | None = None,
    regex: bool = False,
    preciza: bool = False,
    limo: int = 10,
    ordo: str = "nivelo",
    uuid: bool = False,
) -> list[dict[str, Any]]:
    """Execute search and return results.

    Args:
        Same as serci CLI command parameters.

    Returns:
        List of matching entry dicts.
    """
    service = get_service()

    # Build filters dict from non-None values
    filters: dict[str, Any] = {}
    if ligilo:
        pass  # TODO: implement link-based search
    if lingvo:
        filters["lingvo"] = lingvo
    if tipo:
        filters["tipo"] = tipo
    if temo:
        filters["temo"] = temo
    if tono:
        filters["tono"] = tono
    if verko:
        filters["verko"] = verko
    if autoro:
        filters["autoro"] = autoro
    if nivelo_min:
        filters["nivelo_min"] = nivelo_min
    if nivelo_max:
        filters["nivelo_max"] = nivelo_max
    # Convert partial date tokens to ISO range (start/end of day)
    range_filters: dict[str, tuple[str | None, str | None]] | None = None
    if dato_de or dato_gis:
        iso_start, iso_end = date_range(dato_de, dato_gis)
        range_filters = {"kreita_je": (iso_start, iso_end)}

    if teksto is None and not filters and not range_filters:
        entries = service.list(order_by=ordo, desc=False, limit=limo)
    else:
        entries = service.search_advanced(
            query=teksto or "",
            filters=filters,
            fuzzy=not preciza and not regex,
            limit=limo,
            range_filters=range_filters,
        )

    return entries


def _display_search_results(
    entries: list[dict[str, Any]],
    uuid: bool = False,
) -> list[dict[str, Any]] | None:
    """Display search results and optionally let user select one.

    If multiple results, presents an interactive numbered table
    via select_candidate() and returns the selected entry.
    If single result, displays it directly.

    Args:
        entries: Search results list.
        uuid: If True, output UUIDs as JSON and return None.

    Returns:
        The selected entry if user picked one, or None.
    """
    if not entries:
        info(tr_multi("Neniuj rezultoj", "No results", "Aucun resultat"))
        return None

    if uuid:
        import json

        uuids = [e["uuid"][:8] for e in entries]
        console.print(json.dumps(uuids))
        return None

    if len(entries) == 1:
        return entries[0]

    # Multiple results: show interactive selection
    result = select_candidate(
        entries,
        columns=[
            {"header": "UUID", "style": "dim", "width": 10},
            {"header": "Teksto"},
            {"header": "Lingvo", "style": "dim", "width": 6},
        ],
        row_formatter=lambda e, i: [
            e.get("uuid", "")[:8],
            e.get("teksto", ""),
            e.get("lingvo", "") or "",
        ],
    )
    if result is not None:
        idx, _ = result
        return entries[idx]

    return None


__all__ = ["_run_search", "_display_search_results"]