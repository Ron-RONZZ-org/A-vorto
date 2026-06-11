"""Inline reference resolution and linked entry display."""

from __future__ import annotations

import re
from typing import Any

from A.utils.output import console
from A.core.references import resolve as resolve_ref


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
        if m.group(2):
            uuid = m.group(2)
            full_match = m.group(0)
            if full_match.startswith("[") and "(ec#" in full_match.lower():
                return _resolve_cross_module("ec", uuid, label)
            elif full_match.startswith("[") and "(vt#" in full_match.lower():
                return _resolve_cross_module("vt", uuid, label)
            target = service.get(uuid)
            if target:
                return label or target.get("teksto", "")
            return m.group(0)
        elif m.group(3):
            uuid = m.group(3)
            target = service.get(uuid)
            if target:
                return target.get("teksto", "")
            return m.group(0)
        elif m.group(4):
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
        Resolved display text (label or title), or original ref if unresolvable.
    """
    resolved = resolve_ref(prefix, uuid)
    if resolved and resolved.exists and resolved.title:
        return label or resolved.title
    return label or f"{prefix}#{uuid[:8]}"


def _try_cross_module_fallback(uuid: str) -> str | None:
    """Try to resolve a bare UUID against known cross-module types.

    Args:
        uuid: UUID to resolve (8+ hex chars).

    Returns:
        Display title if found, None otherwise.
    """
    for prefix in ("ec", "vt"):
        resolved = resolve_ref(prefix, uuid)
        if resolved and resolved.exists and resolved.title:
            return resolved.title
    return None


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
        console.print("[bold]Ligiloj (elirantaj):[/]")
        for line in outgoing_lines:
            console.print(line)

    incoming_lines: list[str] = []
    for link in links.get("incoming", []):
        source = service.get(link.source_id)
        title = source.get("teksto", "") if source else link.source_id[:8]
        incoming_lines.append(f"  ← {title} ({link.source_id[:8]})")
    if incoming_lines:
        console.print("[bold]Ligiloj (envenantaj):[/]")
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
