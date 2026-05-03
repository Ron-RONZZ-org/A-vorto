"""CLI for vorto command."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from A import error, info, tr_multi
from A.core.import_ import import_json
from A.core.export import export_json, export_toml
from A.utils.output import console, print_table

from A_vorto.service import get_service

app = typer.Typer(
    name="vorto",
    help=tr_multi(
        "Mia Vorto — persona vortaro-mikroapo.",
        "Mia Vorto — personal wordbook microapp.",
        "Mia Vorto — microapplication de vocabulaire personnel.",
    ),
    no_args_is_help=False,
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help", "--helpo"]},
)


@app.command()
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
    uuid: str,
    html: bool = typer.Option(
        False,
        "--html",
        "-h",
        help=tr_multi("Open markdown as HTML preview in browser", "Open markdown as HTML preview in browser", "Ouvrir le markdown en apercu HTML dans le navigateur"),
    ),
    ref: bool = typer.Option(
        False,
        "--ref",
        "-r",
        help=tr_multi("Show linked entries and references", "Show linked entries and references", "Montrer les entrees liees et les references"),
    ),
    show_all: bool = typer.Option(
        False,
        "--show-all",
        "-a",
        "--cxio",
        help=tr_multi("Show all fields (including empty)", "Show all fields (including empty)", "Afficher tous les champs (y compris vides)"),
    ),
) -> None:
    """View a word entry by UUID."""
    service = get_service()
    entry = service.get(uuid)

    if not entry:
        error(tr_multi(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise typer.Exit(1)

    # Display entry
    console.print(f"[bold cyan]UUID:[/] {entry.get('uuid')}")
    console.print(f"[bold cyan]Teksto:[/] {entry.get('teksto')}")

    # Show all fields or only non-empty
    def show_field(label: str, value) -> bool:
        """Check if field should be displayed."""
        if show_all:
            return True  # Show all in show-all mode
        # Otherwise show if value exists
        if value is None:
            return False
        if isinstance(value, (str, list, dict)):
            return bool(value)
        return True

    if show_field("Lingvo", entry.get("lingvo")):
        val = entry.get("lingvo") or tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Lingvo:[/] {val}")
    if show_field("Kategorio", entry.get("kategorio")):
        val = entry.get("kategorio") or tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Kategorio:[/] {val}")

    tipo = entry.get("tipo")
    if show_field("Tipo", tipo):
        if tipo:
            if isinstance(tipo, list):
                display_tipo = ", ".join(str(t) for t in tipo)
            else:
                display_tipo = str(tipo)
        else:
            display_tipo = tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Tipo:[/] {display_tipo}")

    if show_field("Temo", entry.get("temo")):
        val = entry.get("temo") or tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Temo:[/] {val}")
    if show_field("Tono", entry.get("tono")):
        val = entry.get("tono") or tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Tono:[/] {val}")
    if show_field("Nivelo", entry.get("nivelo")):
        val = entry.get("nivelo") if entry.get("nivelo") is not None else tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Nivelo:[/] {val}")
    if show_field("Autoro", entry.get("autoro")):
        val = entry.get("autoro") or tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Autoro:[/] {val}")
    if show_field("Verko", entry.get("verko")):
        val = entry.get("verko") or tr_multi("(malplena)", "(empty)", "(vide)")
        console.print(f"[bold cyan]Verko:[/] {val}")

    # Show definitions with usage examples
    difinoj = entry.get("difinoj") or []
    uzoj = entry.get("uzoj") or []
    if show_field("Difinoj", difinoj):
        if difinoj:
            console.print("[bold cyan]Difinoj:[/]")
            for i, d in enumerate(difinoj):
                label = f"  {i + 1}. {d}"
                if i < len(uzoj) and uzoj[i]:
                    label += f"  [dim]-- {uzoj[i]}[/]"
                console.print(label)
        else:
            console.print(f"[bold cyan]Difinoj:[/]  {tr_multi('(malplena)', '(empty)', '(vide)')}")

    # Show tags
    etikedoj = entry.get("etikedoj") or {}
    if show_field("Etikedoj", etikedoj):
        if etikedoj and isinstance(etikedoj, dict):
            console.print(f"[bold cyan]Etikedoj:[/]")
            for k, v in etikedoj.items():
                console.print(f"  {k}: {v}")
        else:
            console.print(f"[bold cyan]Etikedoj:[/]  {tr_multi('(malplena)', '(empty)', '(vide)')}")

    # Show links (as resolved references when show_all, as UUIDs otherwise)
    ligiloj = entry.get("ligiloj") or []
    if show_field("Ligiloj", ligiloj):
        if ligiloj:
            console.print(f"[bold cyan]Ligiloj:[/]")
            for ref in ligiloj:
                # Try to resolve the linked entry
                target = service.get(ref)
                if target:
                    title = target.get("teksto", "")
                    console.print(f"  → {title} ({ref[:8]})")
                else:
                    console.print(f"  {ref[:8]} (ne trovita)")
        else:
            console.print(f"[bold cyan]Ligiloj:[/]  {tr_multi('(malplena)', '(empty)', '(vide)')}")

    # Show linked entries and references if --ref flag is set
    if ref:
        # Get links from A.core.links
        links = service.get_linked_entries(uuid)
        
        if links["outgoing"]:
            console.print("[bold cyan]Ligiloj (elirantaj):[/]")
            for link in links["outgoing"]:
                target = service.get(link.target_id)
                title = target.get("teksto", "") if target else link.target_id[:8]
                console.print(f"  → {title} ({link.target_id[:8]})")
        
        if links["incoming"]:
            console.print("[bold cyan]Ligiloj (envenantaj):[/]")
            for link in links["incoming"]:
                source = service.get(link.source_id)
                title = source.get("teksto", "") if source else link.source_id[:8]
                console.print(f"  ← {title} ({link.source_id[:8]})")
        
        # Parse cross-references from text fields
        refs = service.get_references(entry)
        if refs:
            console.print("[bold cyan]Referencoj:[/]")
            for r in refs:
                display = r.title or f"{r.ref_type}#{r.uuid[:8]}"
                exists_mark = "[green]✓[/]" if r.exists else "[red]?[/]"
                console.print(f"  {exists_mark} {display}")

    # Open browser preview if requested
    if html and entry.get("teksto"):
        from A.core.markdown_html_view import preview_markdown
        preview_markdown(entry["teksto"], title=entry["teksto"])

    # Show timestamps
    if show_all:
        console.print(f"[bold cyan]Kreita:[/] {entry.get('kreita_je') or tr_multi('(nekonata)', '(unknown)', '(inconnu)')}")
        console.print(f"[bold cyan]Modifita:[/] {entry.get('modifita_je') or tr_multi('(nekonata)', '(unknown)', '(inconnu)')}")
    else:
        console.print(f"[bold cyan]Kreita:[/] {entry.get('kreita_je')}")
        console.print(f"[bold cyan]Modifita:[/] {entry.get('modifita_je')}")


@app.command("aldoni")
def aldoni(
    teksto: str = typer.Argument(..., help=tr_multi("Word text", "Word text", "Texte du mot")),
    lingvo: Optional[str] = typer.Option(None, "--lingvo", "-l", help=tr_multi("Language", "Language", "Langue")),
    kategorio: Optional[str] = typer.Option(None, "--kategorio", "-k", help=tr_multi("Category (auto-detected if omitted)", "Category (auto-detected if omitted)", "Categorie (auto-detectee si omise)")),
    tipo: Optional[str] = typer.Option(None, "--tipo", help=tr_multi("Type abbreviation(s), comma/semicolon-separated (e.g. su,aj)", "Type abbreviation(s), comma/semicolon-separated (e.g. su,aj)", "Abreviation(s) de type, separees par virgule/point-virgule")),
    temo: Optional[str] = typer.Option(None, "--temo", help=tr_multi("Theme", "Theme", "Theme")),
    tono: Optional[str] = typer.Option(None, "--tono", help=tr_multi("Tonality (e.g. nf, fo, am)", "Tonality (e.g. nf, fo, am)", "Tonalite (ex. nf, fo, am)")),
    difinoj: Optional[List[str]] = typer.Option(None, "--difino", help=tr_multi("Definition with optional usage: difino:{uzo}", "Definition with optional usage: difino:{uzo}", "Definition avec usage optionnel: difino:{uzo}")),
    uzoj: Optional[List[str]] = typer.Option(None, "--uzo", help=tr_multi("Usage example (standalone, no paired definition)", "Usage example (standalone, no paired definition)", "Exemple d'usage (autonome, sans definition associee)")),
    etikedoj: Optional[List[str]] = typer.Option(None, "--etikedo", help=tr_multi("Tag in key:value format", "Tag in key:value format", "Etiquette au format cle:valeur")),
    autoro: Optional[str] = typer.Option(None, "--autoro", help=tr_multi("Author", "Author", "Auteur")),
    verko: Optional[str] = typer.Option(None, "--verko", help=tr_multi("Work/source", "Work/source", "Oeuvre/source")),
    nivelo: Optional[float] = typer.Option(None, "--nivelo", help=tr_multi("Proficiency level (0.0-5.0)", "Proficiency level (0.0-5.0)", "Niveau de competence (0.0-5.0)")),
    ligiloj: Optional[List[str]] = typer.Option(None, "--ligilo", help=tr_multi("Link to UUID(s)", "Link to UUID(s)", "Lier a UUID(s)")),
) -> None:
    """Add a new word entry."""
    from A_vorto.utils import (
        detect_kategorio,
        normalize_tipo,
        normalize_tono,
        parse_etikedoj,
        split_difino_uzo,
    )

    service = get_service()

    # Auto-detect kategorio if not provided
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
        data["tipo"] = effective_tipo
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

    # Add ligiloj (links to other entries)
    if ligiloj:
        data["ligiloj"] = list(ligiloj)

    entry = service.create(data)
    info(tr_multi(f"Aldonis {teksto}", f"Added {teksto}", f"Ajoute {teksto}"))
    console.print(f"[green]UUID:[/] {entry.get('uuid')}")


@app.command("modifi")
def modifi(
    uuid: str,
    teksto: Optional[str] = typer.Option(None, "--teksto", "-t", help=tr_multi("New word text", "New word text", "Nouveau texte")),
    lingvo: Optional[str] = typer.Option(None, "--lingvo", "-l", help=tr_multi("Language", "Language", "Langue")),
    kategorio: Optional[str] = typer.Option(None, "--kategorio", "-k", help=tr_multi("Category", "Category", "Categorie")),
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
    from A_vorto.utils import normalize_tipo, normalize_tono, parse_etikedoj, split_difino_uzo

    service = get_service()

    # Check exists
    existing = service.get(uuid)
    if not existing:
        error(tr_multi(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise typer.Exit(1)

    # Build update data
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
            data["tipo"] = effective
    if clear_tipo:
        data["tipo"] = []

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

    if not data:
        error(tr_multi("Neniuj sxangoj", "No changes", "Aucun changement"))
        raise typer.Exit(1)

    entry = service.update(uuid, data)
    info(tr_multi(f"Modifikas {uuid}", f"Modified {uuid}", f"Modifie {uuid}"))


@app.command("forigi")
def forigi(
    uuid: str,
    hard: bool = typer.Option(
        False,
        "--hard",
        "-H",
        help=tr_multi("Permanent delete (no trash)", "Permanent delete (no trash)", "Suppression permanente"),
    ),
) -> None:
    """Delete a word entry."""
    service = get_service()
    
    existing = service.get(uuid)
    if not existing:
        error(tr_multi(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise typer.Exit(1)
    
    soft = not hard
    service.delete(uuid, soft=soft)
    
    if soft:
        info(tr_multi(f"Forigas {uuid} (sxoveblas)", f"Deleted {uuid} (soft)", f"Supprime {uuid} ( mou)"))
    else:
        info(tr_multi(f"Forigas {uuid} (permanenta)", f"Deleted {uuid} (permanent)", f"Supprime {uuid} (permanent)"))


@app.command("malfari")
def malfari() -> None:
    """Undo the last operation."""
    service = get_service()
    result = service.undo()
    
    if not result:
        info(tr_multi("Nenio por malfari", "Nothing to undo", "Rien a defaire"))
        return
    
    op_type = result.get("operation", "unknown")
    info(tr_multi(f"Malfaris {op_type}", f"Undid {op_type}", f"Defait {op_type}"))


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
    service = get_service()
    entries = service.get_trash(limit=limit)
    
    if not entries:
        info(tr_multi("Rubujo estas cxirkau", "Trash is empty", "Corbeille vide"))
        return
    
    for entry in entries:
        uuid = entry.get("uuid", "")[:8]
        teksto = entry.get("teksto", "")
        forigita = entry.get("forigita_je", "")
        console.print(f"[cyan]{uuid}[/] [bold]{teksto}[/] [dim]{forigita}[/]")
    
    info(tr_multi(f"{len(entries)} en rubujo", f"{len(entries)} in trash", f"{len(entries)} dans la corbeille"))


@app.command("restaurigi")
def restaurigi(
    uuid: str,
) -> None:
    """Restore an entry from trash."""
    service = get_service()
    
    entry = service.restore(uuid)
    if not entry:
        error(tr_multi(f"Vorto {uuid} ne trovitas en rubujo", f"Word {uuid} not found in trash", f"Mot {uuid} non trouve dans la corbeille"))
        raise typer.Exit(1)
    
    info(tr_multi(f"Restaurigis {uuid}", f"Restored {uuid}", f"Restored {uuid}"))


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
    service = get_service()
    
    count = service.empty_trash(days=days)
    info(tr_multi(f"Forigis {count} el rubujo", f"Deleted {count} from trash", f"Supprime {count} de la corbeille"))


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
    service = get_service()
    
    try:
        records = import_json(path, decryption_password=password)
    except Exception as e:
        error(tr_multi(f"Importo fiaskis: {e}", f"Import failed: {e}", f"Echec de l'importation: {e}"))
        raise typer.Exit(1)
    
    count = 0
    for record in records:
        try:
            service.create(record)
            count += 1
        except Exception:
            pass  # Skip duplicates/errors
    
    info(tr_multi(f"Importis {count} vortojn", f"Imported {count} words", f"Importe {count} mots"))


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
    service = get_service()
    
    entries = service.list()
    
    try:
        if formato == "toml":
            export_toml(path, entries, encryption_password=password)
        else:
            export_json(path, entries, encryption_password=password)
    except Exception as e:
        error(tr_multi(f"Eksporto fiaskis: {e}", f"Export failed: {e}", f"Echec de l'exportation: {e}"))
        raise typer.Exit(1)
    
    info(tr_multi(f"Eksportis {len(entries)} vortojn al {path}", f"Exported {len(entries)} words to {path}", f"Exporte {len(entries)} mots vers {path}"))


@app.command("serci")
@app.command("serchi", deprecated=True)
def serci(
    query: str,
    fuzzy: bool = typer.Option(
        False,
        "--fuzzy",
        "-f",
        help=tr_multi("Enable fuzzy matching", "Enable fuzzy matching", "Activer la recherche floue"),
    ),
    limit: Optional[int] = typer.Option(
        20,
        "--limit",
        "-l",
        help=tr_multi("Limit results", "Limit results", "Limiter les resultats"),
    ),
    lingvo: Optional[str] = typer.Option(
        None,
        "--lingvo",
        "-L",
        help=tr_multi("Filter by language", "Filter by language", "Filtrer par langue"),
    ),
    kategorio: Optional[str] = typer.Option(
        None,
        "--kategorio",
        "-k",
        help=tr_multi("Filter by category (vorto/frazo/frazdaro)", "Filter by category (vorto/frazo/frazdaro)", "Filtrer par categorie"),
    ),
    tipo: Optional[str] = typer.Option(
        None,
        "--tipo",
        "-t",
        help=tr_multi("Filter by type (su, aj, etc.)", "Filter by type (su, aj, etc.)", "Filtrer par type"),
    ),
    temo: Optional[str] = typer.Option(
        None,
        "--temo",
        "-m",
        help=tr_multi("Filter by theme", "Filter by theme", "Filtrer par theme"),
    ),
    tono: Optional[str] = typer.Option(
        None,
        "--tono",
        "-T",
        help=tr_multi("Filter by tonality (nf, fo, am)", "Filter by tonality (nf, fo, am)", "Filtrer par tonalite"),
    ),
) -> None:
    """Search word entries using FTS5 full-text search."""
    service = get_service()
    
    # Build filters dict from non-None values
    filters = {}
    if lingvo:
        filters["lingvo"] = lingvo
    if kategorio:
        filters["kategorio"] = kategorio
    if tipo:
        filters["tipo"] = tipo
    if temo:
        filters["temo"] = temo
    if tono:
        filters["tono"] = tono
    
    entries = service.search_advanced(query, filters=filters, fuzzy=fuzzy, limit=limit)
    
    if not entries:
        info(tr_multi("Neniuj rezultoj", "No results", "Aucun resultat"))
        return
    
    for entry in entries:
        uuid = entry.get("uuid", "")[:8]
        teksto = entry.get("teksto", "")
        console.print(f"[cyan]{uuid}[/] [bold]{teksto}[/]")
    
    info(tr_multi(f"{len(entries)} rezultoj", f"{len(entries)} results", f"{len(entries)} resultats"))


__all__ = ["app"]