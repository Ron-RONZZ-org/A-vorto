"""Search command for A-vorto."""

from __future__ import annotations

import typer

from A import tr_multi
from A_vorto.service import get_service
from A_vorto.search_helpers import _run_search, _display_search_results
from A_vorto.display_helpers import _show_entry


def serci(
    teksto: str | None = typer.Argument(
        None,
        help=tr_multi(
            "Text to search (default: show all)",
            "Text to search (default: show all)",
            "Texte a rechercher (par defaut: tout afficher)",
        ),
    ),
    ligilo: str | None = typer.Option(
        None,
        "-L",
        "--ligilo",
        help=tr_multi(
            "Search related entries from UUID/title via links",
            "Search related entries from UUID/title via links",
            "Rechercher des entrees liees via UUID/titre",
        ),
    ),
    lingvo: str | None = typer.Option(
        None,
        "-l",
        "--lingvo",
        help=tr_multi(
            "Filter by language code",
            "Filter by language code",
            "Filtrer par code de langue",
        ),
    ),
    tipo: str | None = typer.Option(
        None,
        "-t",
        "--tipo",
        help=tr_multi(
            "Filter by subtype",
            "Filter by subtype",
            "Filtrer par sous-type",
        ),
    ),
    temo: str | None = typer.Option(
        None,
        "--temo",
        help=tr_multi("Filter by theme", "Filter by theme", "Filtrer par theme"),
    ),
    tono: str | None = typer.Option(
        None,
        "--tono",
        help=tr_multi(
            "Filter by tonality",
            "Filter by tonality",
            "Filtrer par tonalite",
        ),
    ),
    autoro: str | None = typer.Option(
        None,
        "-a",
        "--autoro",
        help=tr_multi(
            "Filter by author",
            "Filter by author",
            "Filtrer par auteur",
        ),
    ),
    verko: str | None = typer.Option(
        None,
        "-v",
        "--verko",
        help=tr_multi(
            "Filter by work (Title:Year format)",
            "Filter by work (Title:Year format)",
            "Filtrer par oeuvre (format Titre:Annee)",
        ),
    ),
    nivelo_min: float | None = typer.Option(
        None,
        "--nivelo-min",
        help=tr_multi(
            "Minimum lexical level",
            "Minimum lexical level",
            "Niveau lexical minimum",
        ),
    ),
    nivelo_max: float | None = typer.Option(
        None,
        "--nivelo-max",
        help=tr_multi(
            "Maximum lexical level",
            "Maximum lexical level",
            "Niveau lexical maximum",
        ),
    ),
    dato_de: str | None = typer.Option(
        None,
        "--dato-de",
        help=tr_multi(
            "Start date YYYY-MM-DD",
            "Start date YYYY-MM-DD",
            "Date de debut AAAA-MM-JJ",
        ),
    ),
    dato_gis: str | None = typer.Option(
        None,
        "--dato-gis",
        help=tr_multi(
            "End date YYYY-MM-DD",
            "End date YYYY-MM-DD",
            "Date de fin AAAA-MM-JJ",
        ),
    ),
    regex: bool = typer.Option(
        False,
        "-r",
        "--regex",
        help=tr_multi(
            "Interpret text as POSIX regex",
            "Interpret text as POSIX regex",
            "Interpreter le texte comme regex POSIX",
        ),
    ),
    preciza: bool = typer.Option(
        False,
        "-p",
        "--preciza",
        help=tr_multi(
            "Disable fuzzy fallback",
            "Disable fuzzy fallback",
            "Desactiver la recherche floue",
        ),
    ),
    limo: int = typer.Option(
        10,
        "-lo",
        "--limo",
        help=tr_multi(
            "Max results (default 10)",
            "Max results (default 10)",
            "Nombre max de resultats (defaut 10)",
        ),
    ),
    ordo: str = typer.Option(
        "nivelo",
        "-o",
        "--ordo",
        help=tr_multi(
            "Order: nivelo/n, dato/d, inversa-dato/id",
            "Order: nivelo/n, dato/d, inversa-dato/id",
            "Ordre: nivelo/n, dato/d, inversa-dato/id",
        ),
    ),
    uuid: bool = typer.Option(
        False,
        "-u",
        "--uuid",
        help=tr_multi(
            "Output only UUID list as JSON",
            "Output only UUID list as JSON",
            "Sortir uniquement la liste UUID en JSON",
        ),
    ),
) -> None:
    """Search word entries. Without args, list entries up to --limo."""
    entries = _run_search(
        teksto=teksto,
        ligilo=ligilo,
        lingvo=lingvo,
        tipo=tipo,
        temo=temo,
        tono=tono,
        autoro=autoro,
        verko=verko,
        nivelo_min=nivelo_min,
        nivelo_max=nivelo_max,
        dato_de=dato_de,
        dato_gis=dato_gis,
        regex=regex,
        preciza=preciza,
        limo=limo,
        ordo=ordo,
        uuid=uuid,
    )

    selected = _display_search_results(entries, uuid=uuid)
    if selected:
        _show_entry(get_service(), selected)


__all__ = ["serci"]
