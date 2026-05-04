"""Helpers for forigi, malfari, rubujo, restaurigi, senrubujigi commands."""

from __future__ import annotations

from typing import Optional

from A import error, info, tr_multi
from A.utils.output import console

from A_vorto.service import get_service


def _handle_forigi(uuid: str, hard: bool = False) -> None:
    """Delete a word entry (soft or permanent).

    Args:
        uuid: Entry UUID.
        hard: If True, permanently delete.
    """
    service = get_service()

    existing = service.get(uuid)
    if not existing:
        error(tr_multi(f"Vorto {uuid} ne trovitas", f"Word {uuid} not found", f"Mot {uuid} non trouve"))
        raise SystemExit(1)

    soft = not hard
    service.delete(uuid, soft=soft)

    if soft:
        info(tr_multi(f"Forigas {uuid} (sxoveblas)", f"Deleted {uuid} (soft)", f"Supprime {uuid} ( mou)"))
    else:
        info(tr_multi(f"Forigas {uuid} (permanenta)", f"Deleted {uuid} (permanent)", f"Supprime {uuid} (permanent)"))


def _handle_malfari() -> None:
    """Undo the last operation."""
    service = get_service()
    result = service.undo()

    if not result:
        info(tr_multi("Nenio por malfari", "Nothing to undo", "Rien a defaire"))
        return

    op_type = result.get("operation", "unknown")
    info(tr_multi(f"Malfaris {op_type}", f"Undid {op_type}", f"Defait {op_type}"))


def _handle_rubujo(limit: Optional[int] = 20) -> None:
    """List entries in trash.

    Args:
        limit: Max entries to show.
    """
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


def _handle_restaurigi(uuid: str) -> None:
    """Restore an entry from trash.

    Args:
        uuid: Entry UUID.
    """
    service = get_service()

    entry = service.restore(uuid)
    if not entry:
        error(tr_multi(f"Vorto {uuid} ne trovitas en rubujo", f"Word {uuid} not found in trash", f"Mot {uuid} non trouve dans la corbeille"))
        raise SystemExit(1)

    info(tr_multi(f"Restaurigis {uuid}", f"Restored {uuid}", f"Restored {uuid}"))


def _handle_senrubujigi(days: int = 30) -> None:
    """Permanently delete entries from trash older than specified days.

    Args:
        days: Delete entries older than this many days.
    """
    service = get_service()
    count = service.empty_trash(days=days)
    info(tr_multi(f"Forigis {count} el rubujo", f"Deleted {count} from trash", f"Supprime {count} de la corbeille"))


__all__ = [
    "_handle_forigi",
    "_handle_malfari",
    "_handle_rubujo",
    "_handle_restaurigi",
    "_handle_senrubujigi",
]