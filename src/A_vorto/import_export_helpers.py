"""Helpers for importi and eksporti commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from A import error, info, tr_multi
from A.core.import_ import import_json
from A.core.export import export_json, export_toml

from A_vorto.service import get_service


def _handle_import(path: Path, password: str | None = None) -> None:
    """Import word entries from JSON file.

    Args:
        path: Path to import file.
        password: Decryption password.
    """
    service = get_service()

    try:
        records = import_json(path, decryption_password=password)
    except Exception as e:
        error(tr_multi(f"Importo fiaskis: {e}", f"Import failed: {e}", f"Echec de l'importation: {e}"))
        raise SystemExit(1)

    count = 0
    for record in records:
        try:
            service.create(record)
            count += 1
        except Exception:
            pass  # Skip duplicates/errors

    info(tr_multi(f"Importis {count} vortojn", f"Imported {count} words", f"Importe {count} mots"))


def _handle_export(path: Path, formato: str = "json", password: str | None = None) -> None:
    """Export word entries to JSON or TOML file.

    Args:
        path: Path to export file.
        formato: Export format (json, toml).
        password: Encryption password.
    """
    service = get_service()
    entries = service.list()

    try:
        if formato == "toml":
            export_toml(path, entries, encryption_password=password)
        else:
            export_json(path, entries, encryption_password=password)
    except Exception as e:
        error(tr_multi(f"Eksporto fiaskis: {e}", f"Export failed: {e}", f"Echec de l'exportation: {e}"))
        raise SystemExit(1)

    info(tr_multi(f"Eksportis {len(entries)} vortojn al {path}", f"Exported {len(entries)} words to {path}", f"Exporte {len(entries)} mots vers {path}"))


__all__ = ["_handle_import", "_handle_export"]