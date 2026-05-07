from A import confirm_action
"""CLI for vorto command."""

from pathlib import Path
from typing import Annotated, List, Optional

import typer

from A import error, info, tr_multi
from A.utils.output import console, print_table

from A_vorto.service import get_service
from A_vorto.display_helpers import _show_entry, _preview_entry
from A_vorto.search_helpers import _run_search, _display_search_results
from A_vorto.modify_helpers import _build_create_data, _build_update_data, _handle_create_result, _find_duplicate
from A_vorto.manage_helpers import _handle_forigi, _handle_malfari, _handle_rubujo, _handle_restaurigi, _handle_senrubujigi
from A_vorto.import_export_helpers import _handle_import, _handle_export


def _display_results(entries: list[dict]) -> None:
    """Display search results in table format."""
    if not entries:
        info(tr_multi("Neniuj rezultoj", "No results", "Aucun resultat"))
        return
    
    columns = [
        {"header": "UUID", "key": "uuid", "style": "dim", "width": 8},
        {"header": "Teksto", "key": "teksto"},
        {"header": "Lingvo", "key": "lingvo"},
    ]
    print_table(columns, entries)

app = typer.Typer(
    name="vorto",
    help=tr_multi(
        "Mia Vorto — persona vortaro-mikroapo.",
        "Mia Vorto — personal wordbook microapp.",
        "Mia Vorto — microapplication de vocabulaire personnel.",
    ),
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help", "--helpo"]},
)


@app.command("ls")
@app.command("list", hidden=True)
def list(
    order_by: str = typer.Option(
        "teksto",
        "--order-by",
        "-o",
        help=tr_multi("Order by field", "Order by field", "Champ de tri"),
    ),
    desc: bool = typer.Option(
        False,
        "--desc",
        "-d",
        help=tr_multi("Descending order", "Descending order", "Ordre decroissant"),
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help=tr_multi("Limit results", "Limit results", "Limiter les resultats"),
    ),
) -> None:
    """List all word entries."""
    service = get_service()
    entries = service.list(order_by=order_by, desc=desc, limit=limit)

    columns = [
        {"header": "UUID", "key": "uuid", "style": "dim", "width": 10},
        {"header": "Teksto", "key": "teksto"},
        {"header": "Lingvo", "key": "lingvo"},
        {"header": "Kategorio", "key": "kategorio"},
    ]

    print_table(columns, entries, title=tr_multi("Vortoj", "Words", "Mots"))


@app.command("vidi")
def vidi(
    uid: str | None = typer.Argument(
        None,
        help=tr_multi("UUID (or prefix) of entry to view. Omit to list latest 50.", "UUID (or prefix) of entry to view. Omit to list latest 50.", "UUID (ou prefixe) de l'entree. Omettre pour lister les 50 dernieres."),
    ),
    teksto: str | None = typer.Option(
        None,
        "-T",
        "--teksto",
        help=tr_multi("Look up by title/text instead of UUID", "Look up by title/text instead of UUID", "Rechercher par titre/texte au lieu de UUID"),
    ),
    inversa: bool = typer.Option(
        False,
        "-i",
        "--inversa",
        help=tr_multi("List oldest 50 first (only without UUID)", "List oldest 50 first (only without UUID)", "Lister les 50 plus anciennes d'abord (sans UUID)"),
    ),
    cxio: bool = typer.Option(
        False,
        "-a",
        "--cxio",
        help=tr_multi("Show all fields (including dates)", "Show all fields (including dates)", "Afficher tous les champs (y compris les dates)"),
    ),
    html: bool = typer.Option(
        False,
        "-H",
        "--html",
        help=tr_multi("Open as HTML preview in browser", "Open as HTML preview in browser", "Ouvrir en apercu HTML dans le navigateur"),
    ),
    ref: bool = typer.Option(
        False,
        "-r",
        "--ref",
        help=tr_multi("Show linked entries and references", "Show linked entries and references", "Montrer les entrees liees et les references"),
    ),
    kopii: bool = typer.Option(
        False,
        "-k",
        "--kopii",
        help=tr_multi("Copy UUID to clipboard", "Copy UUID to clipboard", "Copier UUID dans le presse-papiers"),
    ),
    semantika_kopii: bool = typer.Option(
        False,
        "-sk",
        "--semantika-kopii",
        help=tr_multi("Copy [teksto](uuid) to clipboard", "Copy [teksto](uuid) to clipboard", "Copier [texte](uuid) dans le presse-papiers"),
    ),
) -> None:
    """View a word entry, or list latest 50 entries when called without argument."""
    # Validate arguments
    if uid is not None and teksto is not None:
        error(tr_multi("Use either UUID or --teksto, not both", "Use either UUID or --teksto, not both", "Utiliser UUID ou --teksto, pas les deux"))
        raise typer.Exit(1)
    
    service = get_service()
    
    # Handle clipboard mutual exclusivity
    if kopii and semantika_kopii:
        error(tr_multi("Use only one of --kopii or --semantika-kopii", "Use only one of --kopii or --semantika-kopii", "Utiliser une seule option"))
        raise typer.Exit(1)
    
    # Handle clipboard with invalid UUID
    if (kopii or semantika_kopii) and uid is None:
        error(tr_multi("--kopii/--semantika-kopii requires UUID", "--kopii/--semantika-kopii requires UUID", "--kopii/--semantika-kopii necessite UUID"))
        raise typer.Exit(1)
    
    # No UUID - list latest/oldest 50, or look up by text
    if uid is None:
        if teksto:
            entry = service.find_by_text_prefix(teksto)
            if not entry:
                error(tr_multi(f"Vorto {teksto} ne trovitas", f"Word {teksto} not found", f"Mot {teksto} non trouve"))
                raise typer.Exit(1)
            # Text found - entry is set, fall through to display below
        else:
            entries = service.list(order_by="kreita_je", desc=not inversa, limit=50)
            info(tr_multi(f"{len(entries)} rezulto(j)", f"{len(entries)} result(s)", f"{len(entries)} resultat(s)"))
            _display_results(entries)
            return
    else:
        lookup_uid = uid[1:] if uid and uid.startswith("#") else uid
        entry = service.get(lookup_uid)
        if not entry:
            error(tr_multi(f"Vorto {uid} ne trovitas", f"Word {uid} not found", f"Mot {uid} non trouve"))
            raise typer.Exit(1)
    
    # Display entry using Rich Panel
    _show_entry(service, entry, cxio=cxio, ref=ref, html=html, kopii=kopii, semantika_kopii=semantika_kopii)


@app.command("aldoni")
def aldoni(
    teksto: str = typer.Argument(..., help=tr_multi("Word text", "Word text", "Texte du mot")),
    lingvo: Optional[str] = typer.Option(None, "--lingvo", "-l", help=tr_multi("Language", "Language", "Langue")),
    kategorio: Optional[str] = typer.Option(None, "--kategorio", help=tr_multi("Category (auto-detected if omitted)", "Category (auto-detected if omitted)", "Categorie (auto-detectee si omise)")),
    tipo: Optional[str] = typer.Option(None, "--tipo", "-t", help=tr_multi("Type abbreviation(s), comma/semicolon-separated (e.g. su,aj)", "Type abbreviation(s), comma/semicolon-separated (e.g. su,aj)", "Abreviation(s) de type, separees par virgule/point-virgule")),
    temo: Optional[str] = typer.Option(None, "--temo", help=tr_multi("Theme", "Theme", "Theme")),
    tono: Optional[str] = typer.Option(None, "--tono", help=tr_multi("Tonality (e.g. nf, fo, am)", "Tonality (e.g. nf, fo, am)", "Tonalite (ex. nf, fo, am)")),
    nivelo: Optional[float] = typer.Option(None, "-n", "--nivelo", help=tr_multi("Proficiency level (0.0-5.0)", "Proficiency level (0.0-5.0)", "Niveau de competence (0.0-5.0)")),
    difinoj: Optional[List[str]] = typer.Option(None, "-d", "--difino", help=tr_multi("Definition with optional usage: difino:{uzo}", "Definition with optional usage: difino:{uzo}", "Definition avec usage optionnel: difino:{uzo}")),
    uzoj: Optional[List[str]] = typer.Option(None, "--uzo", help=tr_multi("Usage example (standalone, no paired definition)", "Usage example (standalone, no paired definition)", "Exemple d'usage (autonome, sans definition associee)")),
    etikedoj: Optional[List[str]] = typer.Option(None, "-e", "--etikedo", help=tr_multi("Tag in key:value format", "Tag in key:value format", "Etiquette au format cle:valeur")),
    ligiloj: Optional[List[str]] = typer.Option(None, "-L", "--ligilo", help=tr_multi("Link to UUID(s)", "Link to UUID(s)", "Lier a UUID(s)")),
    autoro: Optional[str] = typer.Option(None, "-A", "--autoro", help=tr_multi("Author", "Author", "Auteur")),
    verko: Optional[str] = typer.Option(None, "-v", "--verko", help=tr_multi("Work/source (Title:Year format)", "Work/source (Title:Year format)", "Oeuvre/source (format Titre:Annee)")),
    kopii: bool = typer.Option(
        False,
        "-k",
        "--kopii",
        help=tr_multi("Copy UUID to clipboard", "Copy UUID to clipboard", "Copier UUID dans le presse-papiers"),
    ),
    semantika_kopii: bool = typer.Option(
        False,
        "-sk",
        "--semantika-kopii",
        help=tr_multi("Copy [teksto](uuid) to clipboard", "Copy [teksto](uuid) to clipboard", "Copier [texte](uuid) dans le presse-papiers"),
    ),
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help=tr_multi("Skip confirmation prompt", "Skip confirmation prompt", "Preterpasi konfirmon"),
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
        info(tr_multi(
            f"Jam ekzistas: \"{existing['teksto']}\" ({existing['uuid'][:8]})",
            f"Already exists: \"{existing['teksto']}\" ({existing['uuid'][:8]})",
            f"Existe deja: \"{existing['teksto']}\" ({existing['uuid'][:8]})",
        ))
        if not yes:
            replace = confirm_action(tr_multi(
                "Anstatauigi la ekzistantan?",
                "Replace the existing entry?",
                "Remplacer l'entree existante?",
            ), default=False)
            if not replace:
                info(tr_multi("Nuligita", "Cancelled", "Annule"))
                return
        # Update existing entry
        entry = service.update(existing["uuid"], data)
        info(tr_multi(f"Gxisdatigis {teksto}", f"Updated {teksto}", f"Mis a jour {teksto}"))
        return

    # Preview before creation
    if not yes:
        _preview_entry(data)
        confirmed = confirm_action(tr_multi(
            "Cxu krei tiun eniron?",
            "Create this entry?",
            "Creer cette entree?",
        ), default=True)
        if not confirmed:
            info(tr_multi("Nuligita", "Cancelled", "Annule"))
            return

    # Create entry
    entry = service.create(data)
    _handle_create_result(entry, teksto, kopii, semantika_kopii)


@app.command("modifi")
def modifi(
    uuid: str = typer.Argument(
        ..., help=tr_multi("UUID (or #UUID) of entry to modify", "UUID (or #UUID) of entry to modify", "UUID (ou #UUID) de l'entree a modifier")
    ),
    teksto: Optional[str] = typer.Option(None, "--teksto", "-t", help=tr_multi("New word text", "New word text", "Nouveau texte")),
    lingvo: Optional[str] = typer.Option(None, "--lingvo", "-l", help=tr_multi("Language", "Language", "Langue")),
    kategorio: Optional[str] = typer.Option(None, "--kategorio", help=tr_multi("Category", "Category", "Categorie")),
    tipo: Optional[str] = typer.Option(None, "--tipo", help=tr_multi("Type abbreviation(s), comma/semicolon-separated", "Type abbreviation(s), comma/semicolon-separated", "Abreviation(s) de type, separees par virgule/point-virgule")),
    temo: Optional[str] = typer.Option(None, "--temo", help=tr_multi("Theme", "Theme", "Theme")),
    tono: Optional[str] = typer.Option(None, "--tono", help=tr_multi("Tonality (e.g. nf, fo, am)", "Tonality (e.g. nf, fo, am)", "Tonalite (ex. nf, fo, am)")),
    difinoj: Optional[List[str]] = typer.Option(None, "--difino", help=tr_multi("Definition with optional usage: difino:{uzo}", "Definition with optional usage: difino:{uzo}", "Definition avec usage optionnel: difino:{uzo}")),
    uzoj: Optional[List[str]] = typer.Option(None, "--uzo", help=tr_multi("Usage example (standalone)", "Usage example (standalone)", "Exemple d'usage (autonome)")),
    etikedoj: Optional[List[str]] = typer.Option(None, "--etikedo", help=tr_multi("Tag in key:value format", "Tag in key:value format", "Etiquette au format cle:valeur")),
    autoro: Optional[str] = typer.Option(None, "--autoro", help=tr_multi("Author", "Author", "Auteur")),
    verko: Optional[str] = typer.Option(None, "--verko", help=tr_multi("Work/source", "Work/source", "Oeuvre/source")),
    nivelo: Optional[float] = typer.Option(None, "--nivelo", help=tr_multi("Proficiency level (0.0-5.0)", "Proficiency level (0.0-5.0)", "Niveau de competence (0.0-5.0)")),
    clear_difinoj: bool = typer.Option(False, "--clear-difinoj", help=tr_multi("Clear all definitions", "Clear all definitions", "Effacer toutes les definitions")),
    clear_uzoj: bool = typer.Option(False, "--clear-uzoj", help=tr_multi("Clear all usage examples", "Clear all usage examples", "Effacer tous les exemples d'usage")),
    clear_etikedoj: bool = typer.Option(False, "--clear-etikedoj", help=tr_multi("Clear all tags", "Clear all tags", "Effacer toutes les etiquettes")),
    clear_ligiloj: bool = typer.Option(False, "--clear-ligiloj", help=tr_multi("Clear all links", "Clear all links", "Effacer tous les liens")),
    clear_tipo: bool = typer.Option(False, "--clear-tipo", help=tr_multi("Clear type list", "Clear type list", "Effacer la liste des types")),
    ligilo_add: Optional[List[str]] = typer.Option(None, "--ligilo-add", help=tr_multi("Add link(s) to UUID(s)", "Add link(s) to UUID(s)", "Ajouter un/des lien(s) a UUID(s)")),
    ligilo_remove: Optional[List[str]] = typer.Option(None, "--ligilo-remove", help=tr_multi("Remove link(s) by UUID", "Remove link(s) by UUID", "Retirer un/des lien(s) par UUID")),
) -> None:
    """Modify a word entry."""
    service = get_service()

    existing = service.get(uuid)
    if not existing:
        error(tr_multi(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise typer.Exit(1)

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
        ligilo_add=ligilo_add,
        ligilo_remove=ligilo_remove,
    )

    if not data:
        error(tr_multi("Neniuj sxangoj", "No changes", "Aucun changement"))
        raise typer.Exit(1)

    entry = service.update(uuid, data)
    info(tr_multi(f"Modifikas {uuid}", f"Modified {uuid}", f"Modifie {uuid}"))


@app.command("forigi")
def forigi(
    uuids: List[str] = typer.Argument(
        ..., help=tr_multi(
            "UUID (or #UUID) of entries to delete (multiple)",
            "UUID (or #UUID) of entries to delete (multiple)",
            "UUID (ou #UUID) des entrees a supprimer (plusieurs)",
        )
    ),
    hard: bool = typer.Option(
        False,
        "--hard",
        "-H",
        help=tr_multi("Permanent delete (no trash)", "Permanent delete (no trash)", "Suppression permanente"),
    ),
) -> None:
    """Delete word entries."""
    for uid in uuids:
        _handle_forigi(uid, hard=hard)


@app.command("malfari")
def malfari() -> None:
    """Undo the last operation."""
    _handle_malfari()


@app.command("rubujo")
def rubujo(
    limit: Optional[int] = typer.Option(
        20,
        "--limit",
        "-l",
        help=tr_multi("Limit results", "Limit results", "Limiter les resultats"),
    ),
) -> None:
    """List entries in trash."""
    _handle_rubujo(limit=limit)


@app.command("restaurigi")
def restaurigi(
    uuid: str = typer.Argument(
        ..., help=tr_multi("UUID (or #UUID) to restore", "UUID (or #UUID) to restore", "UUID (ou #UUID) a restaurer")
    ),
) -> None:
    """Restore an entry from trash."""
    _handle_restaurigi(uuid)


@app.command("senrubujigi")
def senrubujigi(
    days: int = typer.Option(
        30,
        "--days",
        "-d",
        help=tr_multi("Delete entries older than days", "Delete entries older than days", "Supprimer les entrees plus anciennes que jours"),
    ),
) -> None:
    """Permanently delete entries from trash older than specified days."""
    _handle_senrubujigi(days=days)


@app.command("importi")
def importi(
    path: Path = typer.Argument(..., help=tr_multi("Path to import file", "Path to import file", "Chemin du fichier a importer")),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help=tr_multi("Decryption password", "Decryption password", "Mot de passe de decryptage"),
    ),
) -> None:
    """Import word entries from JSON file."""
    _handle_import(path, password=password)


@app.command("eksporti")
def eksporti(
    path: Path = typer.Argument(..., help=tr_multi("Path to export file", "Path to export file", "Chemin du fichier d'exportation")),
    formato: str = typer.Option(
        "json",
        "--format",
        "-f",
        help=tr_multi("Format: json, toml", "Format: json, toml", "Format: json, toml"),
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help=tr_multi("Encryption password", "Encryption password", "Mot de passe de chiffrement"),
    ),
) -> None:
    """Export word entries to JSON or TOML file."""
    _handle_export(path, formato=formato, password=password)


@app.command("serci")
@app.command("serchi", deprecated=True)
def serci(
    teksto: str | None = typer.Argument(
        None,
        help=tr_multi("Text to search (default: show all)", "Text to search (default: show all)", "Texte a rechercher (par defaut: tout afficher)"),
    ),
    ligilo: str | None = typer.Option(
        None,
        "-L",
        "--ligilo",
        help=tr_multi("Search related entries from UUID/title via links", "Search related entries from UUID/title via links", "Rechercher des entrees liees via UUID/titre"),
    ),
    lingvo: str | None = typer.Option(
        None,
        "-l",
        "--lingvo",
        help=tr_multi("Filter by language code", "Filter by language code", "Filtrer par code de langue"),
    ),
    tipo: str | None = typer.Option(
        None,
        "-t",
        "--tipo",
        help=tr_multi("Filter by subtype", "Filter by subtype", "Filtrer par sous-type"),
    ),
    temo: str | None = typer.Option(
        None,
        "--temo",
        help=tr_multi("Filter by theme", "Filter by theme", "Filtrer par theme"),
    ),
    tono: str | None = typer.Option(
        None,
        "--tono",
        help=tr_multi("Filter by tonality", "Filter by tonality", "Filtrer par tonalite"),
    ),
    autoro: str | None = typer.Option(
        None,
        "-a",
        "--autoro",
        help=tr_multi("Filter by author", "Filter by author", "Filtrer par auteur"),
    ),
    verko: str | None = typer.Option(
        None,
        "-v",
        "--verko",
        help=tr_multi("Filter by work (Title:Year format)", "Filter by work (Title:Year format)", "Filtrer par oeuvre (format Titre:Annee)"),
    ),
    nivelo_min: float | None = typer.Option(
        None,
        "--nivelo-min",
        help=tr_multi("Minimum lexical level", "Minimum lexical level", "Niveau lexical minimum"),
    ),
    nivelo_max: float | None = typer.Option(
        None,
        "--nivelo-max",
        help=tr_multi("Maximum lexical level", "Maximum lexical level", "Niveau lexical maximum"),
    ),
    dato_de: str | None = typer.Option(
        None,
        "--dato-de",
        help=tr_multi("Start date YYYY-MM-DD", "Start date YYYY-MM-DD", "Date de debut AAAA-MM-JJ"),
    ),
    dato_gis: str | None = typer.Option(
        None,
        "--dato-gis",
        help=tr_multi("End date YYYY-MM-DD", "End date YYYY-MM-DD", "Date de fin AAAA-MM-JJ"),
    ),
    regex: bool = typer.Option(
        False,
        "-r",
        "--regex",
        help=tr_multi("Interpret text as POSIX regex", "Interpret text as POSIX regex", "Interpreter le texte comme regex POSIX"),
    ),
    preciza: bool = typer.Option(
        False,
        "-p",
        "--preciza",
        help=tr_multi("Disable fuzzy fallback", "Disable fuzzy fallback", "Desactiver la recherche floue"),
    ),
    limo: int = typer.Option(
        10,
        "-lo",
        "--limo",
        help=tr_multi("Max results (default 10)", "Max results (default 10)", "Nombre max de resultats (defaut 10)"),
    ),
    ordo: str = typer.Option(
        "nivelo",
        "-o",
        "--ordo",
        help=tr_multi("Order: nivelo/n, dato/d, inversa-dato/id", "Order: nivelo/n, dato/d, inversa-dato/id", "Ordre: nivelo/n, dato/d, inversa-dato/id"),
    ),
    uuid: bool = typer.Option(
        False,
        "-u",
        "--uuid",
        help=tr_multi("Output only UUID list as JSON", "Output only UUID list as JSON", "Sortir uniquement la liste UUID en JSON"),
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


__all__ = ["app"]