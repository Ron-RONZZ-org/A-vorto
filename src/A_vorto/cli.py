"""CLI for vorto command."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from A import error, info, tr_multi
from A.core.import_ import import_json
from A.core.export import export_json, export_toml
from A.utils import copy_to_clipboard
from A.utils.output import console, print_table

from A_vorto.service import get_service


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
        help=tr_multi("Copy #uuid to clipboard", "Copy #uuid to clipboard", "Copier #uuid dans le presse-papiers"),
    ),
    semantika_kopii: bool = typer.Option(
        False,
        "-sk",
        "--semantika-kopii",
        help=tr_multi("Copy [teksto](#uuid) to clipboard", "Copy [teksto](#uuid) to clipboard", "Copier [texte](#uuid) dans le presse-papiers"),
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
    
    # No UUID - list latest/oldest 50
    if uid is None:
        if teksto:
            # Look up by title
            entry = service.find_by_text_prefix(teksto)
            if not entry:
                error(tr_multi(f"Vorto {teksto} ne trovitas", f"Word {teksto} not found", f"Mot {teksto} non trouve"))
                raise typer.Exit(1)
        else:
            # List entries
            entries = service.list(order_by="kreita_je", desc=not inversa, limit=50)
            info(tr_multi(f"{len(entries)} rezulto(j)", f"{len(entries)} result(s)", f"{len(entries)} resultat(s)"))
            _display_results(entries)
            return
    
    lookup_uid = uid[1:] if uid and uid.startswith("#") else uid
    entry = service.get(lookup_uid)
    
    if not entry:
        # Try fuzzy/closest matches
        # For now, just error
        error(tr_multi(f"Vorto {uid} ne trovitas", f"Word {uid} not found", f"Mot {uid} non trouve"))
        raise typer.Exit(1)
    
    # Handle clipboard copy
    if kopii or semantika_kopii:
        if kopii:
            copy_to_clipboard(f"#{entry['uuid'][:8]}")
        if semantika_kopii:
            copy_to_clipboard(f"[{entry['teksto']}](#{entry['uuid'][:8]})")

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
        help=tr_multi("Copy #uuid to clipboard", "Copy #uuid to clipboard", "Copier #uuid dans le presse-papiers"),
    ),
    semantika_kopii: bool = typer.Option(
        False,
        "-sk",
        "--semantika-kopii",
        help=tr_multi("Copy [teksto](#uuid) to clipboard", "Copy [teksto](#uuid) to clipboard", "Copier [texte](#uuid) dans le presse-papiers"),
    ),
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
    
    # Handle clipboard copy options
    if kopii or semantika_kopii:
        if kopii:
            copy_to_clipboard(f"#{entry['uuid'][:8]}")
        if semantika_kopii:
            copy_to_clipboard(f"[{entry['teksto']}](#{entry['uuid'][:8]})")


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
        "graveco",
        "-o",
        "--ordo",
        help=tr_multi("Order: graveco/g, dato/d, inversa-dato/id", "Order: graveco/g, dato/d, inversa-dato/id", "Ordre: graveco/g, dato/d, inversa-dato/id"),
    ),
    uuid: bool = typer.Option(
        False,
        "-u",
        "--uuid",
        help=tr_multi("Output only UUID list as JSON", "Output only UUID list as JSON", "Sortir uniquement la liste UUID en JSON"),
    ),
) -> None:
    """Search word entries. Without args, list entries up to --limo."""
    service = get_service()
    
    # Build filters dict from non-None values
    filters = {}
    if ligilo:
        # Find linked entries
        linked_entries = []
        # TODO: implement link-based search
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
    
    # Handle date filters
    if dato_de or dato_gis:
        filters["dato_de"] = dato_de
        filters["dato_gis"] = dato_gis
    
    # If no text query and no filters, list entries
    if teksto is None and not filters:
        entries = service.list(order_by=ordo, desc=False, limit=limo)
    else:
        # Use FTS search with filters
        entries = service.search_advanced(
            teksto or "",
            filters=filters,
            fuzzy=not preciza and not regex,
            limit=limo,
        )
    
    if uuid:
        import json
        uuids = [e["uuid"][:8] for e in entries]
        console.print(json.dumps(uuids))
        return
    
    if not entries:
        info(tr_multi("Neniuj rezultoj", "No results", "Aucun resultat"))
        return
    
    for entry in entries:
        uuid = entry.get("uuid", "")[:8]
        teksto = entry.get("teksto", "")
        console.print(f"[cyan]{uuid}[/] [bold]{teksto}[/]")
    
    info(tr_multi(f"{len(entries)} rezultoj", f"{len(entries)} results", f"{len(entries)} resultats"))


__all__ = ["app"]