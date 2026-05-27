"""View command for A-vorto."""

from __future__ import annotations

import re
from typing import Optional

import typer

from A import error, info, tr_multi
from A_vorto.service import get_service
from A_vorto.search_helpers import _run_search, _display_search_results
from A_vorto.display_helpers import _show_entry, _display_results


def vidi(
    uid: str | None = typer.Argument(
        None,
        help=tr_multi(
            "UUID (or prefix) of entry to view. Omit to list latest 50.",
            "UUID (or prefix) of entry to view. Omit to list latest 50.",
            "UUID (ou prefixe) de l'entree. Omettre pour lister les 50 dernieres.",
        ),
    ),
    teksto: str | None = typer.Option(
        None,
        "-T",
        "--teksto",
        help=tr_multi(
            "Look up by title/text instead of UUID",
            "Look up by title/text instead of UUID",
            "Rechercher par titre/texte au lieu de UUID",
        ),
    ),
    inversa: bool = typer.Option(
        False,
        "-i",
        "--inversa",
        help=tr_multi(
            "List oldest 50 first (only without UUID)",
            "List oldest 50 first (only without UUID)",
            "Lister les 50 plus anciennes d'abord (sans UUID)",
        ),
    ),
    cxio: bool = typer.Option(
        False,
        "-a",
        "--cxio",
        help=tr_multi(
            "Show all fields (including dates)",
            "Show all fields (including dates)",
            "Afficher tous les champs (y compris les dates)",
        ),
    ),
    html: bool = typer.Option(
        False,
        "-H",
        "--html",
        help=tr_multi(
            "Open as HTML preview in browser",
            "Open as HTML preview in browser",
            "Ouvrir en apercu HTML dans le navigateur",
        ),
    ),
    ref: bool = typer.Option(
        False,
        "-r",
        "--ref",
        help=tr_multi(
            "Show linked entries and references",
            "Show linked entries and references",
            "Montrer les entrees liees et les references",
        ),
    ),
    kopii: bool = typer.Option(
        False,
        "-k",
        "--kopii",
        help=tr_multi(
            "Copy UUID to clipboard",
            "Copy UUID to clipboard",
            "Copier UUID dans le presse-papiers",
        ),
    ),
    semantika_kopii: bool = typer.Option(
        False,
        "-sk",
        "--semantika-kopii",
        help=tr_multi(
            "Copy [teksto](uuid) to clipboard",
            "Copy [teksto](uuid) to clipboard",
            "Copier [texte](uuid) dans le presse-papiers",
        ),
    ),
) -> None:
    """View a word entry, or list latest 50 entries when called without argument."""
    # Validate arguments
    if uid is not None and teksto is not None:
        error(
            tr_multi(
                "Use either UUID or --teksto, not both",
                "Use either UUID or --teksto, not both",
                "Utiliser UUID ou --teksto, pas les deux",
            )
        )
        raise typer.Exit(1)

    service = get_service()

    # Handle clipboard mutual exclusivity
    if kopii and semantika_kopii:
        error(
            tr_multi(
                "Use only one of --kopii or --semantika-kopii",
                "Use only one of --kopii or --semantika-kopii",
                "Utiliser une seule option",
            )
        )
        raise typer.Exit(1)

    # Handle clipboard with invalid UUID
    if (kopii or semantika_kopii) and uid is None:
        error(
            tr_multi(
                "--kopii/--semantika-kopii requires UUID",
                "--kopii/--semantika-kopii requires UUID",
                "--kopii/--semantika-kopii necessite UUID",
            )
        )
        raise typer.Exit(1)

    # No UUID - list latest/oldest 50, or look up by text
    if uid is None:
        if teksto:
            entry = service.find_by_text_prefix(teksto)
            if not entry:
                error(
                    tr_multi(
                        f"Vorto {teksto} ne trovitas",
                        f"Word {teksto} not found",
                        f"Mot {teksto} non trouve",
                    )
                )
                raise typer.Exit(1)
            # Text found - entry is set, fall through to display below
        else:
            entries = service.list(
                order_by="kreita_je", desc=not inversa, limit=50
            )
            info(
                tr_multi(
                    f"{len(entries)} rezulto(j)",
                    f"{len(entries)} result(s)",
                    f"{len(entries)} resultat(s)",
                )
            )
            _display_results(entries)
            return
    else:
        lookup_uid = uid[1:] if uid and uid.startswith("#") else uid
        entry = service.get(lookup_uid)
        if not entry:
            # Check if input looks like a UUID (all hex, 6+ chars)
            if re.match(r"^[0-9a-fA-F]{6,}$", lookup_uid):
                error(
                    tr_multi(
                        f"Vorto {uid} ne trovitas",
                        f"Word {uid} not found",
                        f"Mot {uid} non trouve",
                    )
                )
                raise typer.Exit(1)
            # Not UUID-like — fall back to text search
            if kopii or semantika_kopii:
                error(
                    tr_multi(
                        "--kopii/--semantika-kopii requires a UUID argument",
                        "--kopii/--semantika-kopii requires a UUID argument",
                        "--kopii/--semantika-kopii necessite un argument UUID",
                    )
                )
                raise typer.Exit(1)
            entries = _run_search(teksto=lookup_uid)
            selected = _display_search_results(entries)
            if not selected:
                raise typer.Exit(1)
            entry = selected
            # Disable clipboard for search fallback
            kopii = False
            semantika_kopii = False

    # Display entry using Rich Panel
    _show_entry(
        service,
        entry,
        cxio=cxio,
        ref=ref,
        html=html,
        kopii=kopii,
        semantika_kopii=semantika_kopii,
    )


__all__ = ["vidi"]
