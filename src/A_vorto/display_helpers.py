"""Display helpers for vidi entry view."""

from __future__ import annotations

import json
from typing import Any

from rich.panel import Panel
from rich.text import Text

from A import tr_multi, copy_to_clipboard
from A.utils.output import console
from A.core.references import resolve as resolve_ref

from A_vorto._display_references import (
    _resolve_inline_refs,
    _resolve_cross_module,
    _try_cross_module_fallback,
    _show_linked_entries,
    _show_references,
)
from A_vorto._display_preview import _preview_entry


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
            copy_to_clipboard(entry['uuid'][:8])
        if semantika_kopii:
            copy_to_clipboard(f"[{entry['teksto']}]({entry['uuid'][:8]})")

    # Build panel title (truncated to console width)
    full_text = str(entry.get("teksto", "") or "")
    max_title_w = max(10, min(50, console.width - 30))
    if len(full_text) > max_title_w:
        display_title = full_text[:max_title_w] + "…"
    else:
        display_title = full_text
    title = Text()
    title.append(display_title, style="bold white")
    title.append(f"  {entry['uuid'][:8]}", style="dim")

    # Build content lines
    lines: list[str] = []

    if len(full_text) > max_title_w:
        lines.append(f"[bold]{full_text}[/]")
        lines.append("")

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

    if show_field("Autoro", entry.get("autoro")):
        lines.append(f"[dim]autoro:[/] {_format_value(entry.get('autoro'))}")
    if show_field("Verko", entry.get("verko")):
        verko_text = _resolve_inline_refs(
            _format_value(entry.get("verko") or ""), service
        )
        lines.append(f"[dim]verko:[/] {verko_text}")

    if cxio:
        if show_field("Temo", entry.get("temo"), cxio):
            temo_text = _resolve_inline_refs(
                _format_value(entry.get("temo") or ""), service
            )
            lines.append(f"[dim]temo:[/] {temo_text}")
        if show_field("Tono", entry.get("tono"), cxio):
            lines.append(f"[dim]tono:[/] {_format_value(entry.get('tono'))}")
        if show_field("Nivelo", entry.get("nivelo"), cxio):
            nivelo = entry.get("nivelo")
            lines.append(f"[dim]nivelo:[/] {f'{nivelo:.1f}' if nivelo is not None else ''}")

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
        rendered_difinoj = [_resolve_inline_refs(d, service) for d in difinoj]
        rendered_uzoj = [_resolve_inline_refs(u, service) for u in uzoj]
        if len(difinoj) == 1:
            section_label += f"\n[bold]{rendered_difinoj[0]}[/]"
            if uzoj and uzoj[0] and rendered_uzoj[0]:
                section_label += f"\n[italic]{rendered_uzoj[0]}[/]"
        else:
            for i, d in enumerate(rendered_difinoj, 1):
                section_label += f"\n[bold]{i}. {d}[/]"
                if i - 1 < len(rendered_uzoj) and rendered_uzoj[i - 1]:
                    section_label += f"\n   [italic]{rendered_uzoj[i - 1]}[/]"
        lines.append(section_label)

    if cxio:
        etikedoj_raw = entry.get("etikedoj") or "{}"
        if isinstance(etikedoj_raw, str):
            etikedoj = json.loads(etikedoj_raw) if etikedoj_raw.strip() else {}
        else:
            etikedoj = etikedoj_raw or {}
        if show_field("Etikedoj", etikedoj, cxio=True):
            tags_parts = [f"[dim]{k}:[/] {v}" for k, v in etikedoj.items()]
            if tags_parts:
                lines.append("\n[bold]etikedoj:[/]\n" + "\n".join(tags_parts))

    ligiloj_raw = entry.get("ligiloj") or "[]"
    if isinstance(ligiloj_raw, str):
        ligiloj = json.loads(ligiloj_raw) if ligiloj_raw.strip() else []
    else:
        ligiloj = ligiloj_raw or []
    if show_field("Ligiloj", ligiloj):
        link_texts: list[str] = []
        for link_ref in ligiloj:
            raw_ref = str(link_ref or "")
            if raw_ref.lower().startswith("ec#") or raw_ref.lower().startswith("vt#"):
                parts = raw_ref.split("#", 1)
                if len(parts) == 2:
                    prefix = parts[0].lower()
                    link_uuid = parts[1]
                    resolved = resolve_ref(prefix, link_uuid)
                    if resolved and resolved.exists and resolved.title:
                        link_texts.append(f"→ {resolved.title} ({prefix}#{link_uuid[:8]})")
                    else:
                        link_texts.append(f"  {prefix}#{link_uuid[:8]} (ne trovita)")
            else:
                target = service.get(link_ref)
                if target:
                    link_texts.append(f"→ {target.get('teksto', '')} ({raw_ref[:8]})")
                else:
                    cross = _try_cross_module_fallback(link_ref)
                    if cross:
                        link_texts.append(f"→ {cross}")
                    else:
                        link_texts.append(f"  {raw_ref[:8]} (ne trovita)")
        if link_texts:
            lines.append("\n".join(link_texts))

    if cxio:
        lines.append(
            f"[dim]kreita:[/] {entry.get('kreita_je') or ''}\n"
            f"[dim]modifita:[/] {entry.get('modifita_je') or ''}"
        )

    content = "\n".join(lines) if lines else ""
    panel = Panel(
        content,
        title=title,
        title_align="left",
        border_style="dim",
        padding=(0, 1),
    )
    console.print(panel)

    if ref:
        _show_linked_entries(service, entry)
        _show_references(service, entry)

    if html and entry.get("teksto"):
        from A.core.markdown_html_view import preview_markdown

        preview_markdown(entry["teksto"], title=entry["teksto"])


__all__ = [
    "show_field",
    "_format_value",
    "_show_entry",
    "_resolve_inline_refs",
    "_resolve_cross_module",
    "_try_cross_module_fallback",
    "_show_linked_entries",
    "_show_references",
    "_preview_entry",
]
