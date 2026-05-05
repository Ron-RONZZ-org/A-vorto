"""Display helpers for vidi entry view."""

from __future__ import annotations

import json
import re
from typing import Any

from rich.panel import Panel
from rich.text import Text

from A import tr_multi, copy_to_clipboard
from A.utils.output import console
from A.core.references import resolve as resolve_ref

# Regex for inline refs: [label](#uuid), [label](ec#uuid), bare #uuid, bare ec#/vt#uuid
_INLINE_REF_RE = re.compile(
    r"\[([^\]]*)\]\((?:#|(?:ec|vt)#)([0-9a-f]{4,})\)"
    r"|#([0-9a-f]{8})"
    r"|\b(ec|vt)#([0-9a-f]{8})\b",
    re.IGNORECASE,
)


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


# Regex for inline refs: [label](#uuid), bare #uuid, ec#uuid, vt#uuid
# Groups: 1=label, 2=uuid_from_markdown, 3=bare_hash_uuid, 4=prefix, 5=prefix_uuid
_INLINE_REF_RE = re.compile(
    r"\[([^\]]*)\]\((?:#|(?:ec|vt)#)([0-9a-f]{4,})\)"
    r"|#([0-9a-f]{8})"
    r"|\b(ec|vt)#([0-9a-f]{8})\b",
    re.IGNORECASE,
)


def _resolve_inline_refs(text: str, service: Any) -> str:
    """Resolve inline refs like #uuid, [label](#uuid), ec#uuid to entry text.

    For cross-module refs (ec#uuid, vt#uuid), uses A.core.references.resolve()
    which can look up entries in both A-vorto and A-encik.

    Args:
        text: Text that may contain references.
        service: Vorto service instance for intra-module UUID resolution.

    Returns:
        Text with resolved references. Unresolvable refs are left unchanged.
    """
    if not text:
        return text

    def _replace(m: re.Match) -> str:
        label = m.group(1) or ""
        # Determine UUID and whether it's a cross-module ref
        if m.group(2):  # [label](#uuid) or [label](ec#uuid) or [label](vt#uuid)
            uuid = m.group(2)
            # Check the original text for ec#/vt# prefix
            full_match = m.group(0)
            if full_match.startswith("[") and "(ec#" in full_match.lower():
                return _resolve_cross_module("ec", uuid, label)
            elif full_match.startswith("[") and "(vt#" in full_match.lower():
                return _resolve_cross_module("vt", uuid, label)
            # Bare #uuid inside markdown link
            target = service.get(uuid)
            if target:
                resolved = label or target.get("teksto", "")
                return f"{resolved} (#{uuid[:8]})"
            return m.group(0)
        elif m.group(3):  # bare #uuid
            uuid = m.group(3)
            target = service.get(uuid)
            if target:
                resolved = label or target.get("teksto", "")
                return f"{resolved} #{uuid[:8]}"
            return m.group(0)
        elif m.group(4):  # ec#uuid or vt#uuid bare ref
            prefix = m.group(4).lower()
            uuid = m.group(5)
            return _resolve_cross_module(prefix, uuid)
        return m.group(0)

    return _INLINE_REF_RE.sub(_replace, text)


def _resolve_cross_module(prefix: str, uuid: str, label: str = "") -> str:
    """Resolve a cross-module ref (ec#uuid or vt#uuid) using A.core.

    Args:
        prefix: "ec" or "vt".
        uuid: UUID to resolve.
        label: Optional label from markdown link.

    Returns:
        Resolved CLI string, or original prefix#uuid if unresolvable.
    """
    resolved = resolve_ref(prefix, uuid)
    if resolved and resolved.exists and resolved.title:
        display = label or resolved.title
        return f"{display} ({prefix}#{uuid[:8]})"
    return label or f"{prefix}#{uuid[:8]}"


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

    # Build panel title
    title = Text()
    title.append(str(entry.get("teksto", "") or ""), style="bold")
    title.append(f"  {entry['uuid'][:8]}", style="dim")

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
            raw_ref = str(link_ref or "")
            # Check for cross-module ref (ec#uuid or vt#uuid)
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
                    link_texts.append(f"  {raw_ref[:8]} (ne trovita)")
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


def _preview_entry(data: dict[str, Any]) -> None:
    """Show a compact text preview of entry data before creation.

    Args:
        data: Entry data dict (teksto, lingvo, tipo, difinoj, etc.)
    """
    lines: list[str] = []
    lines.append(f"[bold]{data.get('teksto', '')}[/]")

    parts: list[str] = []
    if data.get("lingvo"):
        parts.append(str(data["lingvo"]))
    tipo = data.get("tipo", "")
    if tipo:
        parts.append(str(tipo) if isinstance(tipo, str) else ", ".join(tipo))
    if parts:
        lines.append(f"[dim]{' | '.join(parts)}[/]")

    difinoj = data.get("difinoj", [])
    if difinoj:
        if isinstance(difinoj, str):
            try:
                difinoj = json.loads(difinoj)
            except (json.JSONDecodeError, TypeError):
                difinoj = []
        if difinoj:
            lines.append("")
            for d in difinoj[:3]:
                lines.append(f"  {d}")
            if len(difinoj) > 3:
                lines.append(f"  ... ({len(difinoj)} difinoj)")

    for line in lines:
        console.print(line)


__all__ = ["show_field", "_show_entry", "_preview_entry"]