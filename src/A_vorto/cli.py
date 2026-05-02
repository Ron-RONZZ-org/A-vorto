"""CLI for vorto command."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from A import error, info, tr
from A.core.import_ import import_json
from A.core.export import export_json, export_toml
from A.utils.output import console
from A.core.markdown_html_view import markdown_to_html

from A_vorto.service import get_service

app = typer.Typer(
    name="vorto",
    help=tr(
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
        help=tr("Order by field", "Order by field", "Champ de tri"),
    ),
    desc: bool = typer.Option(
        False,
        "--desc",
        "-d",
        help=tr("Descending order", "Descending order", "Ordre decroissant"),
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-l",
        help=tr("Limit results", "Limit results", "Limiter les resultats"),
    ),
) -> None:
    """List all word entries."""
    service = get_service()
    entries = service.list(order_by=order_by, desc=desc, limit=limit)
    
    if not entries:
        info(tr("Neniuj videblas", "No entries found", "Aucune entree"))
        return
    
    for entry in entries:
        uuid = entry.get("uuid", "")[:8]
        teksto = entry.get("teksto", "")
        kategorio = entry.get("kategorio", "")
        console.print(f"[cyan]{uuid}[/] [bold]{teksto}[/] {kategorio}")


@app.command("vidi")
def vidi(
    uuid: str,
    html: bool = typer.Option(
        False,
        "--html",
        "-h",
        help=tr("Render markdown as HTML", "Render markdown as HTML", "Afficher le markdown en HTML"),
    ),
) -> None:
    """View a word entry by UUID."""
    service = get_service()
    entry = service.get(uuid)
    
    if not entry:
        error(tr(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise typer.Exit(1)
    
    # Display full entry
    console.print(f"[bold cyan]UUID:[/] {entry.get('uuid')}")
    console.print(f"[bold cyan]Teksto:[/] {entry.get('teksto')}")
    
    if entry.get("lingvo"):
        console.print(f"[bold cyan]Lingvo:[/] {entry.get('lingvo')}")
    if entry.get("kategorio"):
        console.print(f"[bold cyan]Kategorio:[/] {entry.get('kategorio')}")
    if entry.get("tipo"):
        console.print(f"[bold cyan]Tipo:[/] {entry.get('tipo')}")
    if entry.get("temo"):
        console.print(f"[bold cyan]Temo:[/] {entry.get('temo')}")
    
    # Render markdown preview if requested
    if html and entry.get("teksto"):
        html_output = markdown_to_html(entry["teksto"])
        console.print(f"[bold cyan]HTML:[/]\n{html_output}")
    
    console.print(f"[bold cyan]Kreita:[/] {entry.get('kreita_je')}")
    console.print(f"[bold cyan]Modifita:[/] {entry.get('modifita_je')}")


@app.command("aldoni")
def aldoni(
    teksto: str = typer.Argument(..., help=tr("Word text", "Word text", "Texte du mot")),
    lingvo: Optional[str] = typer.Option(None, "--lingvo", "-l", help=tr("Language", "Language", "Langue")),
    kategorio: Optional[str] = typer.Option(None, "--kategorio", "-k", help=tr("Category", "Category", "Categorie")),
    tipo: Optional[str] = typer.Option(None, "--tipo", help=tr("Type", "Type", "Type")),
    temo: Optional[str] = typer.Option(None, "--temo", help=tr("Theme", "Theme", "Theme")),
) -> None:
    """Add a new word entry."""
    service = get_service()
    
    data = {"teksto": teksto}
    if lingvo:
        data["lingvo"] = lingvo
    if kategorio:
        data["kategorio"] = kategorio
    if tipo:
        data["tipo"] = tipo
    if temo:
        data["temo"] = temo
    
    entry = service.create(data)
    info(tr(f"Aldonis {teksto}", f"Added {teksto}", f"Ajoute {teksto}"))
    console.print(f"[green]UUID:[/] {entry.get('uuid')}")


@app.command("modifi")
def modifi(
    uuid: str,
    teksto: Optional[str] = typer.Option(None, "--teksto", "-t", help=tr("New word text", "New word text", "Nouveau texte")),
    lingvo: Optional[str] = typer.Option(None, "--lingvo", "-l", help=tr("Language", "Language", "Langue")),
    kategorio: Optional[str] = typer.Option(None, "--kategorio", "-k", help=tr("Category", "Category", "Categorie")),
    tipo: Optional[str] = typer.Option(None, "--tipo", help=tr("Type", "Type", "Type")),
    temo: Optional[str] = typer.Option(None, "--temo", help=tr("Theme", "Theme", "Theme")),
) -> None:
    """Modify a word entry."""
    service = get_service()
    
    # Check exists
    existing = service.get(uuid)
    if not existing:
        error(tr(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise typer.Exit(1)
    
    # Build update data
    data = {}
    if teksto:
        data["teksto"] = teksto
    if lingvo is not None:
        data["lingvo"] = lingvo
    if kategorio is not None:
        data["kategorio"] = kategorio
    if tipo is not None:
        data["tipo"] = tipo
    if temo is not None:
        data["temo"] = temo
    
    if not data:
        error(tr("Neniuj sxangoj", "No changes", "Aucun changement"))
        raise typer.Exit(1)
    
    entry = service.update(uuid, data)
    info(tr(f"Modifikas {uuid}", f"Modified {uuid}", f"Modifie {uuid}"))


@app.command("forigi")
def forigi(
    uuid: str,
    hard: bool = typer.Option(
        False,
        "--hard",
        "-H",
        help=tr("Permanent delete (no trash)", "Permanent delete (no trash)", "Suppression permanente"),
    ),
) -> None:
    """Delete a word entry."""
    service = get_service()
    
    existing = service.get(uuid)
    if not existing:
        error(tr(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise typer.Exit(1)
    
    soft = not hard
    service.delete(uuid, soft=soft)
    
    if soft:
        info(tr(f"Forigas {uuid} (sxoveblas)", f"Deleted {uuid} (soft)", f"Supprime {uuid} ( mou)"))
    else:
        info(tr(f"Forigas {uuid} (permanenta)", f"Deleted {uuid} (permanent)", f"Supprime {uuid} (permanent)"))


@app.command("malfari")
def malfari() -> None:
    """Undo the last operation."""
    service = get_service()
    result = service.undo()
    
    if not result:
        info(tr("Nenio por malfari", "Nothing to undo", "Rien a defaire"))
        return
    
    op_type = result.get("operation", "unknown")
    info(tr(f"Malfaris {op_type}", f"Undid {op_type}", f"Defait {op_type}"))


@app.command("rubujo")
def rubujo(
    limit: Optional[int] = typer.Option(
        20,
        "--limit",
        "-l",
        help=tr("Limit results", "Limit results", "Limiter les resultats"),
    ),
) -> None:
    """List entries in trash."""
    service = get_service()
    entries = service.get_trash(limit=limit)
    
    if not entries:
        info(tr("Rubujo estas cxirkau", "Trash is empty", "Corbeille vide"))
        return
    
    for entry in entries:
        uuid = entry.get("uuid", "")[:8]
        teksto = entry.get("teksto", "")
        forigita = entry.get("forigita_je", "")
        console.print(f"[cyan]{uuid}[/] [bold]{teksto}[/] [dim]{forigita}[/]")
    
    info(tr(f"{len(entries)} en rubujo", f"{len(entries)} in trash", f"{len(entries)} dans la corbeille"))


@app.command("restaurigi")
def restaurigi(
    uuid: str,
) -> None:
    """Restore an entry from trash."""
    service = get_service()
    
    entry = service.restore(uuid)
    if not entry:
        error(tr(f"Vorto {uuid} ne trovitas en rubujo", f"Word {uuid} not found in trash", f"Mot {uuid} non trouve dans la corbeille"))
        raise typer.Exit(1)
    
    info(tr(f"Restaurigis {uuid}", f"Restored {uuid}", f"Restored {uuid}"))


@app.command("senrubujigi")
def senrubujigi(
    days: int = typer.Option(
        30,
        "--days",
        "-d",
        help=tr("Delete entries older than days", "Delete entries older than days", "Supprimer les entrees plus anciennes que jours"),
    ),
) -> None:
    """Permanently delete entries from trash older than specified days."""
    service = get_service()
    
    count = service.empty_trash(days=days)
    info(tr(f"Forigis {count} el rubujo", f"Deleted {count} from trash", f"Supprime {count} de la corbeille"))


@app.command("importi")
def importi(
    path: Path = typer.Argument(..., help=tr("Path to import file", "Path to import file", "Chemin du fichier a importer")),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help=tr("Decryption password", "Decryption password", "Mot de passe de decryptage"),
    ),
) -> None:
    """Import word entries from JSON file."""
    service = get_service()
    
    try:
        records = import_json(path, decryption_password=password)
    except Exception as e:
        error(tr(f"Importo fiaskis: {e}", f"Import failed: {e}", f"Echec de l'importation: {e}"))
        raise typer.Exit(1)
    
    count = 0
    for record in records:
        try:
            service.create(record)
            count += 1
        except Exception:
            pass  # Skip duplicates/errors
    
    info(tr(f"Importis {count} vortojn", f"Imported {count} words", f"Importe {count} mots"))


@app.command("eksporti")
def eksporti(
    path: Path = typer.Argument(..., help=tr("Path to export file", "Path to export file", "Chemin du fichier d'exportation")),
    formato: str = typer.Option(
        "json",
        "--format",
        "-f",
        help=tr("Format: json, toml", "Format: json, toml", "Format: json, toml"),
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help=tr("Encryption password", "Encryption password", "Mot de passe de chiffrement"),
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
        error(tr(f"Eksporto fiaskis: {e}", f"Export failed: {e}", f"Echec de l'exportation: {e}"))
        raise typer.Exit(1)
    
    info(tr(f"Eksportis {len(entries)} vortojn al {path}", f"Exported {len(entries)} words to {path}", f"Exporte {len(entries)} mots vers {path}"))


@app.command("serchi")
def serchi(
    query: str,
    fuzzy: bool = typer.Option(
        False,
        "--fuzzy",
        "-f",
        help=tr("Enable fuzzy matching", "Enable fuzzy matching", "Activer la recherche floue"),
    ),
    limit: Optional[int] = typer.Option(
        20,
        "--limit",
        "-l",
        help=tr("Limit results", "Limit results", "Limiter les resultats"),
    ),
) -> None:
    """Search word entries using FTS5 full-text search."""
    service = get_service()
    entries = service.search_advanced(query, fuzzy=fuzzy, limit=limit)
    
    if not entries:
        info(tr("Neniuj rezultoj", "No results", "Aucun resultat"))
        return
    
    for entry in entries:
        uuid = entry.get("uuid", "")[:8]
        teksto = entry.get("teksto", "")
        console.print(f"[cyan]{uuid}[/] [bold]{teksto}[/]")
    
    info(tr(f"{len(entries)} rezultoj", f"{len(entries)} results", f"{len(entries)} resultats"))


__all__ = ["app"]