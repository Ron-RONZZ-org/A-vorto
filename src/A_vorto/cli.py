"""CLI for vorto command."""

from __future__ import annotations

from typing import Optional

import typer

from A import error, info, tr
from A.utils.output import console

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


@app.command("serchi")
def serchi(
    query: str,
    limit: Optional[int] = typer.Option(
        20,
        "--limit",
        "-l",
        help=tr("Limit results", "Limit results", "Limiter les resultats"),
    ),
) -> None:
    """Search word entries."""
    service = get_service()
    entries = service.search("teksto", query, case_sensitive=False)
    
    if limit:
        entries = entries[:limit]
    
    if not entries:
        info(tr("Neniuj rezultoj", "No results", "Aucun resultat"))
        return
    
    for entry in entries:
        uuid = entry.get("uuid", "")[:8]
        teksto = entry.get("teksto", "")
        console.print(f"[cyan]{uuid}[/] [bold]{teksto}[/]")
    
    info(tr(f"{len(entries)} rezultoj", f"{len(entries)} results", f"{len(entries)} resultats"))


__all__ = ["app"]