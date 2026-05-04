"""Display helpers for vidi entry view."""

from __future__ import annotations

import json
from typing import Any

from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.console import Group

from A import tr_multi, copy_to_clipboard
from A.utils.output import console
from A.core.markdown_parser import render_markdown


def show_field(label: str, value: Any, cxio: bool = False) -> bool:
    """Check if field should be displayed based on value and display mode.

    Args:
        label: Field label (unused, for consistency).
        value: The field value to check.
        cxio: If True, show all fields regardless of value.

    Returns:
        True if the field should be displayed.
    """
    if cxio:
        return True
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return bool(value)
    return True


def _format_value(value: Any, empty_label: str = "") -> str:
    """Format a value for display, with fallback for empty values.

    Args:
        value: The value to format.
        empty_label: Label to show when value is empty/None.

    Returns:
        Formatted string.
    """
    if value is None or value == "" or value == [] or value == {}:
        return empty_label or tr_multi("(malplena)", "(empty)", "(vide)")
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def _show_entry(
    service: Any,
    entry: dict[str, Any],
    cxio: bool = False,
    ref: bool = False,
    html: bool = False,
    kopii: bool = False,
    semantika_kopii: bool = False,
) -> None:
    """Display a word entry using a Rich Panel with formatted content.

    Args:
        service: VortoService instance for resolving links.
        entry: Entry dict from the database.
        cxio: Show all fields.
        ref: Show linked entries and references.
        html: Open as HTML preview.
        kopii: Copy #uuid to clipboard.
        semantika_kopii: Copy [teksto](#uuid) to clipboard.
    """
    # Handle clipboard copy
    if kopii or semantika_kopii:
        if kopii:
            copy_to_clipboard(f"#{entry['uuid'][:8]}")
        if semantika_kopii:
            copy_to_clipboard(f"[{entry['teksto']}](#{entry['uuid'][:8]})")

    # Build panel title
    title = Text()
    title.append(str(entry.get("teksto", "") or ""), style="bold")
    title.append(f"  #{entry['uuid'][:8]}", style="dim")

    # Build content lines
    lines: list[str] = []

    # Language and type info
    lang = entry.get("lingvo") or ""
    kategorio = entry.get("kategorio") or ""
    tipo = entry.get("tipo") or ""
    tipo_str = ""
    if isinstance(tipo, list):
        tipo_str = ", ".join(tipo)
    elif isinstance(tipo, str):
        tipo_str = tipo

    type_info = "/".join(filter(None, [kategorio, tipo_str]))
    if lang and type_info:
        lines.append(f"[dim]{lang}[/] - [bold]{type_info}[/]")
    elif lang:
        lines.append(f"[bold]{lang}[/]")
    elif type_info:
        lines.append(f"[bold]{type_info}[/]")

    # Metadata rows
    if show_field("Autoro", entry.get("autoro")):
        lines.append(f"[dim]autoro:[/] {_format_value(entry.get('autoro'))}")
    if show_field("Verko", entry.get("verko")):
        lines.append(f"[dim]verko:[/] {_format_value(entry.get('verko'))}")

    if cxio:
        if show_field("Temo", entry.get("temo"), cxio):
            lines.append(f"[dim]temo:[/] {_format_value(entry.get('temo'))}")
        if show_field("Tono", entry.get("tono"), cxio):
            lines.append(f"[dim]tono:[/] {_format_value(entry.get('tono'))}")
        if show_field("Nivelo", entry.get("nivelo"), cxio):
            nivelo = entry.get("nivelo")
            lines.append(f"[dim]nivelo:[/] {f'{nivelo:.1f}' if nivelo is not None else ''}")

    # Definitions with usage examples
    difinoj_raw = entry.get("difinoj") or "[]"
    uzoj_raw = entry.get("uzoj") or "[]"
    if isinstance(difinoj_raw, str):
        difinoj = json.loads(difinoj_raw) if difinoj_raw.strip() else []
    else:
        difinoj = difinoj_raw or []
    if isinstance(uzoj_raw, str):
        uzoj = json.loads(uzoj_raw) if uzoj_raw.strip() else []
    else:
        uzoj = uzoj_raw or []

    if show_field("Difinoj", difinoj):
        section_label = "\n[bold]difinoj:[/]"
        if len(difinoj) == 1:
            rendered = render_markdown(difinoj[0])
            section_label += f"\n{rendered}"
            if uzoj and uzoj[0]:
                section_label += f"\n[italic]{uzoj[0]}[/]"
        else:
            for i, d in enumerate(difinoj, 1):
                rendered = render_markdown(d)
                section_label += f"\n{i}. {rendered}"
                if i - 1 < len(uzoj) and uzoj[i - 1]:
                    section_label += f"\n   [italic]{uzoj[i - 1]}[/]"
        lines.append(section_label)

    # Tags (show in cxio mode only)
    if cxio:
        etikedoj_raw = entry.get("etikedoj") or "{}"
        if isinstance(etikedoj_raw, str):
            etikedoj = json.loads(etikedoj_raw) if etikedoj_raw.strip() else {}
        else:
            etikedoj = etikedoj_raw or {}
        if show_field("Etikedoj", etikedoj, cxio=True):
            tags_parts = [f"[dim]{k}:[/] {v}" for k, v in etikedoj.items()]
            if tags_parts:
                lines.append(f"\n[bold]etikedoj:[/]\n" + "\n".join(tags_parts))

    # Links
    ligiloj_raw = entry.get("ligiloj") or "[]"
    if isinstance(ligiloj_raw, str):
        ligiloj = json.loads(ligiloj_raw) if ligiloj_raw.strip() else []
    else:
        ligiloj = ligiloj_raw or []
    if show_field("Ligiloj", ligiloj):
        link_texts: list[str] = []
        for link_ref in ligiloj:
            target = service.get(link_ref)
            if target:
                link_texts.append(f"→ {target.get('teksto', '')} ({link_ref[:8]})")
            else:
                link_texts.append(f"  {link_ref[:8]} (ne trovita)")
        if link_texts:
            lines.append("\n".join(link_texts))

    # Timestamps
    if cxio:
        lines.append(
            f"[dim]kreita:[/] {entry.get('kreita_je') or ''}\n"
            f"[dim]modifita:[/] {entry.get('modifita_je') or ''}"
        )

    # Build panel
    content = "\n".join(lines) if lines else ""
    panel = Panel(
        content,
        title=title,
        title_align="left",
        border_style="dim",
        padding=(0, 1),
    )
    console.print(panel)

    # Show linked entries and references if --ref flag
    if ref:
        _show_linked_entries(service, entry)
        _show_references(service, entry)

    # Open browser preview if requested
    if html and entry.get("teksto"):
        from A.core.markdown_html_view import preview_markdown

        preview_markdown(entry["teksto"], title=entry["teksto"])


def _show_linked_entries(service: Any, entry: dict[str, Any]) -> None:
    """Show outgoing and incoming links for the entry.

    Args:
        service: VortoService instance.
        entry: Entry dict.
    """
    links = service.get_linked_entries(entry["uuid"])

    outgoing_lines: list[str] = []
    for link in links.get("outgoing", []):
        target = service.get(link.target_id)
        title = target.get("teksto", "") if target else link.target_id[:8]
        outgoing_lines.append(f"  → {title} ({link.target_id[:8]})")
    if outgoing_lines:
        console.print(f"[bold]Ligiloj (elirantaj):[/]")
        for line in outgoing_lines:
            console.print(line)

    incoming_lines: list[str] = []
    for link in links.get("incoming", []):
        source = service.get(link.source_id)
        title = source.get("teksto", "") if source else link.source_id[:8]
        incoming_lines.append(f"  ← {title} ({link.source_id[:8]})")
    if incoming_lines:
        console.print(f"[bold]Ligiloj (envenantaj):[/]")
        for line in incoming_lines:
            console.print(line)


def _show_references(service: Any, entry: dict[str, Any]) -> None:
    """Show cross-references from text fields.

    Args:
        service: VortoService instance.
        entry: Entry dict.
    """
    refs = service.get_references(entry)
    if refs:
        console.print("[bold]Referencoj:[/]")
        for r in refs:
            display = r.title or f"{r.ref_type}#{r.uuid[:8]}"
            exists_mark = "[green]✓[/]" if r.exists else "[red]?[/]"
            console.print(f"  {exists_mark} {display}")


__all__ = ["show_field", "_show_entry"]