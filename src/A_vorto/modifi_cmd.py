"""Modifi command for A-vorto."""

from __future__ import annotations

from typing import List, Optional

import typer

from A import error, info, tr_multi
from A_vorto.service import get_service
from A_vorto.modify_helpers import _build_update_data


def modifi(
    uuid: str = typer.Argument(
        ...,
        help=tr_multi(
            "UUID (or #UUID) of entry to modify",
            "UUID (or #UUID) of entry to modify",
            "UUID (ou #UUID) de l'entree a modifier",
        ),
    ),
    teksto: Optional[str] = typer.Option(
        None,
        "--teksto",
        "-t",
        help=tr_multi("New word text", "New word text", "Nouveau texte"),
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
        help=tr_multi("Category", "Category", "Categorie"),
    ),
    tipo: Optional[str] = typer.Option(
        None,
        "--tipo",
        help=tr_multi(
            "Type abbreviation(s), comma/semicolon-separated",
            "Type abbreviation(s), comma/semicolon-separated",
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
    difinoj: Optional[List[str]] = typer.Option(
        None,
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
            "Usage example (standalone)",
            "Usage example (standalone)",
            "Exemple d'usage (autonome)",
        ),
    ),
    etikedoj: Optional[List[str]] = typer.Option(
        None,
        "--etikedo",
        help=tr_multi(
            "Tag in key:value format",
            "Tag in key:value format",
            "Etiquette au format cle:valeur",
        ),
    ),
    autoro: Optional[str] = typer.Option(
        None,
        "--autoro",
        help=tr_multi("Author", "Author", "Auteur"),
    ),
    verko: Optional[str] = typer.Option(
        None,
        "--verko",
        help=tr_multi(
            "Work/source",
            "Work/source",
            "Oeuvre/source",
        ),
    ),
    nivelo: Optional[float] = typer.Option(
        None,
        "--nivelo",
        help=tr_multi(
            "Proficiency level (0.0-5.0)",
            "Proficiency level (0.0-5.0)",
            "Niveau de competence (0.0-5.0)",
        ),
    ),
    clear_difinoj: bool = typer.Option(
        False,
        "--clear-difinoj",
        help=tr_multi(
            "Clear all definitions",
            "Clear all definitions",
            "Effacer toutes les definitions",
        ),
    ),
    clear_uzoj: bool = typer.Option(
        False,
        "--clear-uzoj",
        help=tr_multi(
            "Clear all usage examples",
            "Clear all usage examples",
            "Effacer tous les exemples d'usage",
        ),
    ),
    clear_etikedoj: bool = typer.Option(
        False,
        "--clear-etikedoj",
        help=tr_multi(
            "Clear all tags",
            "Clear all tags",
            "Effacer toutes les etiquettes",
        ),
    ),
    clear_ligiloj: bool = typer.Option(
        False,
        "--clear-ligiloj",
        help=tr_multi(
            "Clear all links",
            "Clear all links",
            "Effacer tous les liens",
        ),
    ),
    clear_tipo: bool = typer.Option(
        False,
        "--clear-tipo",
        help=tr_multi(
            "Clear type list",
            "Clear type list",
            "Effacer la liste des types",
        ),
    ),
    ligilo_add: Optional[List[str]] = typer.Option(
        None,
        "--ligilo-add",
        help=tr_multi(
            "Add link(s) to UUID(s), #UUID, ec#ref, vt#ref, or text",
            "Add link(s) to UUID(s), #UUID, ec#ref, vt#ref, or text",
            "Ajouter un/des lien(s) a UUID(s), #UUID, ec#ref, vt#ref, ou texte",
        ),
    ),
    ligilo_remove: Optional[List[str]] = typer.Option(
        None,
        "--ligilo-remove",
        help=tr_multi(
            "Remove link(s) by UUID, #UUID, or text",
            "Remove link(s) by UUID, #UUID, or text",
            "Retirer un/des lien(s) par UUID, #UUID, ou texte",
        ),
    ),
) -> None:
    """Modify a word entry."""
    service = get_service()

    existing = service.get(uuid)
    if not existing:
        error(
            tr_multi(
                f"Vorto {uuid} ne trovitas",
                f"Word {uuid} not found",
                f"Mot {uuid} non trouve",
            )
        )
        raise typer.Exit(1)

    # Resolve ligilo refs (text -> UUID, #uuid, ec#, etc.) before set operations
    resolved_add = service.resolve_ligilo_refs(ligilo_add) if ligilo_add else None
    resolved_remove = service.resolve_ligilo_refs(ligilo_remove) if ligilo_remove else None

    data = _build_update_data(
        existing=existing,
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
        autoro=autoro,
        verko=verko,
        clear_difinoj=clear_difinoj,
        clear_uzoj=clear_uzoj,
        clear_etikedoj=clear_etikedoj,
        clear_ligiloj=clear_ligiloj,
        clear_tipo=clear_tipo,
        ligilo_add=resolved_add,
        ligilo_remove=resolved_remove,
    )

    if not data:
        error(
            tr_multi(
                "Neniuj ŝanĝoj",
                "No changes",
                "Aucun changement",
            )
        )
        raise typer.Exit(1)

    entry = service.update(uuid, data)
    info(
        tr_multi(
            f"Modifikas {uuid}",
            f"Modified {uuid}",
            f"Modifie {uuid}",
        )
    )


__all__ = ["modifi"]
