"""Preview display for entry creation."""

from __future__ import annotations

import json
from typing import Any

from A.utils.output import console


def _preview_entry(data: dict[str, Any]) -> None:
    """Show a full, aligned preview of entry data before creation.

    Displays all fields from the data dict with consistent indentation
    and formatting. Preceded by 2 blank lines for visual separation.

    Args:
        data: Entry data dict (teksto, lingvo, tipo, difinoj, etc.)
    """
    lines: list[str] = ["", ""]

    def add_field(label: str, value: Any) -> None:
        if value is not None and value != "" and value != [] and value != {}:
            if isinstance(value, str):
                lines.append(f"  [dim]{label}:[/]  {value}")
            elif isinstance(value, (int, float)):
                lines.append(f"  [dim]{label}:[/]  {value}")

    def add_list_field(label: str, values: list) -> None:
        if not values:
            return
        lines.append("")
        lines.append(f"  [bold]{label}:[/]")
        for i, v in enumerate(values, 1):
            if isinstance(v, str):
                lines.append(f"    {i}. {v}")

    def add_tags_field(label: str, tags: Any) -> None:
        if not tags:
            return
        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except (json.JSONDecodeError, TypeError):
                return
        if not tags:
            return
        lines.append("")
        lines.append(f"  [bold]{label}:[/]")
        if isinstance(tags, dict):
            for k, v in tags.items():
                lines.append(f"    [dim]{k}:[/] {v}")

    teksto = data.get("teksto", "")
    lines.append(f"  [bold]{teksto}[/]")

    info_parts: list[str] = []
    if data.get("lingvo"):
        info_parts.append(str(data["lingvo"]))
    if data.get("kategorio"):
        info_parts.append(str(data["kategorio"]))
    tipo = data.get("tipo")
    if tipo:
        tipo_str = str(tipo) if isinstance(tipo, str) else ", ".join(tipo)
        info_parts.append(tipo_str)
    if info_parts:
        lines.append(f"  [dim]{' | '.join(info_parts)}[/]")

    add_field("temo", data.get("temo"))
    add_field("tono", data.get("tono"))
    add_field("nivelo", data.get("nivelo"))
    add_field("autoro", data.get("autoro"))
    add_field("verko", data.get("verko"))

    difinoj = data.get("difinoj", [])
    if isinstance(difinoj, str):
        try:
            difinoj = json.loads(difinoj)
        except (json.JSONDecodeError, TypeError):
            difinoj = []
    if difinoj:
        lines.append("")
        lines.append("  [bold]difinoj:[/]")
        for i, d in enumerate(difinoj, 1):
            lines.append(f"    {i}. {d}")

    uzoj = data.get("uzoj", [])
    if isinstance(uzoj, str):
        try:
            uzoj = json.loads(uzoj)
        except (json.JSONDecodeError, TypeError):
            uzoj = []
    if uzoj:
        lines.append("")
        lines.append("  [bold]uzoj:[/]")
        for i, u in enumerate(uzoj, 1):
            lines.append(f"    {i}. {u}")

    add_tags_field("etikedoj", data.get("etikedoj"))

    ligiloj = data.get("ligiloj", [])
    if isinstance(ligiloj, str):
        try:
            ligiloj = json.loads(ligiloj)
        except (json.JSONDecodeError, TypeError):
            ligiloj = []
    if ligiloj:
        lines.append("")
        lines.append("  [bold]ligiloj:[/]")
        for link in ligiloj[:10]:
            lines.append(f"    → {link[:50]}")

    for line in lines:
        console.print(line)
