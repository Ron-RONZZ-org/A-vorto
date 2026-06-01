"""Aldoni command for A-vorto."""

from __future__ import annotations

from typing import List, Optional

import typer

from A import confirm_action, info, tr_multi
from A_vorto.service import get_service
from A_vorto.modify_helpers import (
    _build_create_data,
    _find_duplicate,
    _handle_create_result,
)
from A_vorto.display_helpers import _preview_entry


def aldoni(
    teksto: str = typer.Argument(
        ...,
        help=tr_multi("Word text", "Word text", "Texte du mot"),
    ),
    lingvo: Optional[str] = typer.Option(
        None,
        "--lingvo",
        "-l",
        help=tr_multi("Language", "Language", "Langue"),
    ),
    kategorio: Optional[str] = typer.Option(
        None,
        "--kategorio",
        help=tr_multi(
            "Category (auto-detected if omitted)",
            "Category (auto-detected if omitted)",
            "Categorie (auto-detectee si omise)",
        ),
    ),
    tipo: Optional[str] = typer.Option(
        None,
        "--tipo",
        "-t",
        help=tr_multi(
            "Type abbreviation(s), comma/semicolon-separated (e.g. su,aj)",
            "Type abbreviation(s), comma/semicolon-separated (e.g. su,aj)",
            "Abreviation(s) de type, separees par virgule/point-virgule",
        ),
    ),
    temo: Optional[str] = typer.Option(
        None,
        "--temo",
        help=tr_multi("Theme", "Theme", "Theme"),
    ),
    tono: Optional[str] = typer.Option(
        None,
        "--tono",
        help=tr_multi(
            "Tonality (e.g. nf, fo, am)",
            "Tonality (e.g. nf, fo, am)",
            "Tonalite (ex. nf, fo, am)",
        ),
    ),
    nivelo: Optional[float] = typer.Option(
        None,
        "-n",
        "--nivelo",
        help=tr_multi(
            "Proficiency level (0.0-5.0)",
            "Proficiency level (0.0-5.0)",
            "Niveau de competence (0.0-5.0)",
        ),
    ),
    difinoj: Optional[List[str]] = typer.Option(
        None,
        "-d",
        "--difino",
        help=tr_multi(
            "Definition with optional usage: difino::uzo",
            "Definition with optional usage: difino::uzo",
            "Definition avec usage optionnel: difino::uzo",
        ),
    ),
    uzoj: Optional[List[str]] = typer.Option(
        None,
        "--uzo",
        help=tr_multi(
            "Usage example (standalone, no paired definition)",
            "Usage example (standalone, no paired definition)",
            "Exemple d'usage (autonome, sans definition associee)",
        ),
    ),
    etikedoj: Optional[List[str]] = typer.Option(
        None,
        "-e",
        "--etikedo",
        help=tr_multi(
            "Tag in key:value format",
            "Tag in key:value format",
            "Etiquette au format cle:valeur",
        ),
    ),
    ligiloj: Optional[List[str]] = typer.Option(
        None,
        "-L",
        "--ligilo",
        help=tr_multi(
            "Link to UUID(s), #UUID, ec#ref, vt#ref, or text (e.g. -L saluton)",
            "Link to UUID(s), #UUID, ec#ref, vt#ref, or text (e.g. -L saluton)",
            "Lier a UUID(s), #UUID, ec#ref, vt#ref, ou texte (ex. -L saluton)",
        ),
    ),
    autoro: Optional[str] = typer.Option(
        None,
        "-A",
        "--autoro",
        help=tr_multi("Author", "Author", "Auteur"),
    ),
    verko: Optional[str] = typer.Option(
        None,
        "-v",
        "--verko",
        help=tr_multi(
            "Work/source (Title:Year format)",
            "Work/source (Title:Year format)",
            "Oeuvre/source (format Titre:Annee)",
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
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help=tr_multi(
            "Skip confirmation prompt",
            "Skip confirmation prompt",
            "Preterpasi konfirmon",
        ),
    ),
) -> None:
    """Add a new word entry. Checks for duplicates and confirms before creating."""
    service = get_service()

    # Build creation data
    data = _build_create_data(
        teksto=teksto,
        lingvo=lingvo,
        kategorio=kategorio,
        tipo=tipo,
        temo=temo,
        tono=tono,
        nivelo=nivelo,
        difinoj=difinoj,
        uzoj=uzoj,
        etikedoj=etikedoj,
        ligiloj=ligiloj,
        autoro=autoro,
        verko=verko,
    )

    # Check for duplicate by teksto
    existing = _find_duplicate(teksto)
    if existing:
        info(
            tr_multi(
                f'Jam ekzistas: "{existing["teksto"]}" ({existing["uuid"][:8]})',
                f'Already exists: "{existing["teksto"]}" ({existing["uuid"][:8]})',
                f'Existe deja: "{existing["teksto"]}" ({existing["uuid"][:8]})',
            )
        )
        if not yes:
            replace = confirm_action(
                tr_multi(
                    "Anstatauigi la ekzistantan?",
                    "Replace the existing entry?",
                    "Remplacer l'entree existante?",
                ),
                default=False,
            )
            if not replace:
                info(tr_multi("Nuligita", "Cancelled", "Annule"))
                return
        # Update existing entry
        entry = service.update(existing["uuid"], data)
        info(
            tr_multi(
                f"Gxisdatigis {teksto}",
                f"Updated {teksto}",
                f"Mis a jour {teksto}",
            )
        )
        return

    # Preview before creation
    if not yes:
        _preview_entry(data)
        confirmed = confirm_action(
            tr_multi(
                "Cxu krei tiun eniron?",
                "Create this entry?",
                "Creer cette entree?",
            ),
            default=True,
        )
        if not confirmed:
            info(tr_multi("Nuligita", "Cancelled", "Annule"))
            return

    # Create entry
    entry = service.create(data)
    _handle_create_result(entry, teksto, kopii, semantika_kopii)


__all__ = ["aldoni"]
