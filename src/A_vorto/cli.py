"""CLI for vorto command."""

from pathlib import Path
from typing import List, Optional

import typer

from A import error, info, tr_multi
from A.utils.output import print_table

from A_vorto.service import get_service
from A_vorto.manage_helpers import (
    _handle_forigi,
    _handle_malfari,
    _handle_rubujo,
    _handle_restaurigi,
    _handle_senrubujigi,
)
from A_vorto.import_export_helpers import _handle_import, _handle_export

# Fat commands extracted to their own modules for readability (< 200 lines each)
from A_vorto.aldoni_cmd import aldoni as aldoni_func
from A_vorto.modifi_cmd import modifi as modifi_func
from A_vorto.vidi_cmd import vidi as vidi_func
from A_vorto.serci_cmd import serci as serci_func

# Interactive review command
from A_vorto.recenzi_cmd import recenzi as recenzi_func
from A_vorto.recenzi_cmd import historio_app as recenzi_historio_app

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


# Register fat commands extracted to their own modules
app.command(name="vidi")(vidi_func)
app.command(name="aldoni")(aldoni_func)
app.command(name="modifi")(modifi_func)
app.command(name="serci")(serci_func)
app.command(name="serchi", deprecated=True)(serci_func)

# Review command (flat: `vorto recenzi`) + history sub-typer
app.command(name="recenzi", rich_help_panel="Recenzi")(recenzi_func)
app.add_typer(recenzi_historio_app, name="recenzi-historio", rich_help_panel="Recenzi")


@app.command("forigi")
def forigi(
    uuids: List[str] = typer.Argument(
        ...,
        help=tr_multi(
            "UUID (or #UUID) of entries to delete (multiple)",
            "UUID (or #UUID) of entries to delete (multiple)",
            "UUID (ou #UUID) des entrees a supprimer (plusieurs)",
        ),
    ),
    hard: bool = typer.Option(
        False,
        "--hard",
        "-H",
        help=tr_multi(
            "Permanent delete (no trash)",
            "Permanent delete (no trash)",
            "Suppression permanente",
        ),
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
        ...,
        help=tr_multi(
            "UUID (or #UUID) to restore",
            "UUID (or #UUID) to restore",
            "UUID (ou #UUID) a restaurer",
        ),
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
        help=tr_multi(
            "Delete entries older than days",
            "Delete entries older than days",
            "Supprimer les entrees plus anciennes que jours",
        ),
    ),
) -> None:
    """Permanently delete entries from trash older than specified days."""
    _handle_senrubujigi(days=days)


@app.command("importi")
def importi(
    path: Path = typer.Argument(
        ...,
        help=tr_multi(
            "Path to import file",
            "Path to import file",
            "Chemin du fichier a importer",
        ),
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help=tr_multi(
            "Decryption password",
            "Decryption password",
            "Mot de passe de decryptage",
        ),
    ),
) -> None:
    """Import word entries from JSON file."""
    _handle_import(path, password=password)


@app.command("eksporti")
def eksporti(
    path: Path = typer.Argument(
        ...,
        help=tr_multi(
            "Path to export file",
            "Path to export file",
            "Chemin du fichier d'exportation",
        ),
    ),
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
        help=tr_multi(
            "Encryption password",
            "Encryption password",
            "Mot de passe de chiffrement",
        ),
    ),
) -> None:
    """Export word entries to JSON or TOML file."""
    _handle_export(path, formato=formato, password=password)


__all__ = ["app"]
