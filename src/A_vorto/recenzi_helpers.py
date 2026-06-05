"""Review helpers for the recenzi (interactive review) command.

Supports multiple review modes:
- difinoj: show definitions + usage examples, advance with Enter
- tajpu: show definition, user types the word
- multobla: 4-option multiple choice

Also manages review session history (save, list, view, delete, clear).
"""

from __future__ import annotations

import json
import random
import time
import uuid as uuid_mod
from datetime import datetime, timezone
from typing import Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from A import error, info, success, tr_multi
from A.utils.output import console
from A_vorto.data.storage import get_db

# ── Distractor helpers ────────────────────────────────────────────────────────


def _get_same_type_distractors(
    entry: dict[str, Any],
    count: int,
    service: Any,
) -> list[dict[str, Any]]:
    """Get random entries with the same tipo value (excluding *entry*).

    Args:
        entry: The correct entry to exclude.
        count: Number of distractors to fetch.
        service: VortoService instance.

    Returns:
        List of up to *count* distractor entry dicts.
    """
    tipo = entry.get("tipo") or ""
    if not tipo:
        return []

    db = get_db()
    rows = db.execute(
        """SELECT uuid, teksto FROM vorto
           WHERE tipo = ? AND uuid != ? AND forigita_je IS NULL
           ORDER BY RANDOM() LIMIT ?""",
        (tipo, entry["uuid"], count),
    )
    return [dict(r) for r in rows]


# ── Review modes ──────────────────────────────────────────────────────────────


def _recenzi_difinoj(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Mode 1: show definitions + usage examples, Enter to advance.

    Args:
        entries: List of entry dicts to review.

    Returns:
        Stats dict: {entute, gustaj, malgustaj, rezultoj: [...]}
    """
    stats: dict[str, Any] = {
        "entute": len(entries),
        "gustaj": 0,
        "malgustaj": 0,
        "rezultoj": [],
    }
    for entry in entries:
        console.print()
        _show_review_header(entry, len(entries), stats["gustaj"] + stats["malgustaj"] + 1)

        # Show the word
        console.print(f"[bold]{entry.get('teksto', '')}[/]")

        # Show difinoj
        difinoj = _parse_json_field(entry, "difinoj")
        if difinoj:
            console.print("\n[bold]difinoj:[/]")
            for d in difinoj:
                console.print(f"  • {d}")

        # Show uzoj
        uzoj = _parse_json_field(entry, "uzoj")
        if uzoj:
            console.print("\n[italic]uzoj:[/]")
            for u in uzoj:
                console.print(f"  {u}")

        typer.prompt("", default="")
        stats["gustaj"] += 1  # difinoj mode is self-paced, counts as correct
        stats["rezultoj"].append({
            "vorto_uuid": entry["uuid"],
            "gxusta": 1,
            "respondo": "",
            "tempo_sekundoj": 0.0,
        })

    return stats


def _recenzi_tajpu(
    entries: list[dict[str, Any]],
    service: Any,
) -> dict[str, Any]:
    """Mode 2: show definition, user types the word.

    Args:
        entries: List of entry dicts to review.
        service: VortoService for resolving references.

    Returns:
        Stats dict.
    """
    stats: dict[str, Any] = {
        "entute": len(entries),
        "gustaj": 0,
        "malgustaj": 0,
        "rezultoj": [],
    }
    for entry in entries:
        console.print()
        _show_review_header(entry, len(entries), stats["gustaj"] + stats["malgustaj"] + 1)

        # Show difinoj (hide word)
        difinoj = _parse_json_field(entry, "difinoj")
        if difinoj:
            console.print("[bold]difinoj:[/]")
            for d in difinoj:
                console.print(f"  • {d}")
        uzoj = _parse_json_field(entry, "uzoj")
        if uzoj:
            console.print("\n[italic]uzoj:[/]")
            for u in uzoj:
                console.print(f"  {u}")

        correct = entry.get("teksto", "").strip()
        start = time.time()
        answer = typer.prompt("\nVia respondo", default="").strip()
        elapsed = time.time() - start

        if answer.lower() == correct.lower():
            success(tr_multi("GXuste! ✓", "Correct! ✓", "Correct ! ✓"))
            stats["gustaj"] += 1
            stats["rezultoj"].append({
                "vorto_uuid": entry["uuid"],
                "gxusta": 1,
                "respondo": answer,
                "tempo_sekundoj": elapsed,
            })
        else:
            error(tr_multi(
                f"Malĝuste. La ĝusta respondo: {correct}",
                f"Incorrect. The correct answer: {correct}",
                f"Incorrect. La bonne réponse : {correct}",
            ))
            stats["malgustaj"] += 1
            stats["rezultoj"].append({
                "vorto_uuid": entry["uuid"],
                "gxusta": 0,
                "respondo": answer,
                "tempo_sekundoj": elapsed,
            })

    return stats


def _recenzi_multobla(
    entries: list[dict[str, Any]],
    service: Any,
) -> dict[str, Any]:
    """Mode 3: 4-option multiple choice (correct + 3 same-type distractors).

    Args:
        entries: List of entry dicts to review.
        service: VortoService for getting distractors.

    Returns:
        Stats dict.
    """
    stats: dict[str, Any] = {
        "entute": len(entries),
        "gustaj": 0,
        "malgustaj": 0,
        "rezultoj": [],
    }
    for entry in entries:
        console.print()
        _show_review_header(entry, len(entries), stats["gustaj"] + stats["malgustaj"] + 1)

        # Show difinoj (hide word)
        difinoj = _parse_json_field(entry, "difinoj")
        if difinoj:
            console.print("[bold]difinoj:[/]")
            for d in difinoj:
                console.print(f"  • {d}")
        uzoj = _parse_json_field(entry, "uzoj")
        if uzoj:
            console.print("\n[italic]uzoj:[/]")
            for u in uzoj:
                console.print(f"  {u}")

        correct = entry.get("teksto", "").strip()

        # Build options: correct + 3 distractors
        distractors = _get_same_type_distractors(entry, 3, service)
        options = [correct] + [d.get("teksto", "") for d in distractors]
        random.shuffle(options)

        # Pad with more random entries if distractors < 3
        if len(options) < 4:
            extra = service.list(limit=10)
            for e in extra:
                t = e.get("teksto", "").strip()
                if t and t not in options:
                    options.append(t)
                if len(options) >= 4:
                    break

        correct_idx = options.index(correct)

        # Display options
        console.print()
        for i, opt in enumerate(options, 1):
            marker = "✓" if i == correct_idx + 1 else " "
            console.print(f"  {i}. [{marker}] {opt}")

        start = time.time()
        raw = typer.prompt("\nVia elekto (numero)", default="").strip()
        elapsed = time.time() - start

        try:
            choice = int(raw) - 1
        except (ValueError, IndexError):
            choice = -1

        if choice == correct_idx:
            success(tr_multi("GXuste! ✓", "Correct! ✓", "Correct ! ✓"))
            stats["gustaj"] += 1
            stats["rezultoj"].append({
                "vorto_uuid": entry["uuid"],
                "gxusta": 1,
                "respondo": options[choice] if 0 <= choice < len(options) else "",
                "tempo_sekundoj": elapsed,
            })
        else:
            error(tr_multi(
                f"Malĝuste. La ĝusta respondo: {correct}",
                f"Incorrect. The correct answer: {correct}",
                f"Incorrect. La bonne réponse : {correct}",
            ))
            stats["malgustaj"] += 1
            stats["rezultoj"].append({
                "vorto_uuid": entry["uuid"],
                "gxusta": 0,
                "respondo": options[choice] if 0 <= choice < len(options) else "",
                "tempo_sekundoj": elapsed,
            })

    return stats


# ── Display helpers ───────────────────────────────────────────────────────────


def _show_review_header(entry: dict[str, Any], total: int, current: int) -> None:
    """Show a compact header for the current review card."""
    lang = entry.get("lingvo") or ""
    tipo = entry.get("tipo") or ""
    meta = "/".join(filter(None, [lang, tipo]))
    header = f"[bold]{current}/{total}[/]"
    if meta:
        header += f"  [dim]{meta}[/]"
    console.print(header)
    console.print("─" * min(50, console.width))


def _celebrate(stats: dict[str, Any]) -> None:
    """Display a celebration/statistics screen at the end of a session.

    Args:
        stats: Stats dict from the review mode.
    """
    total = stats["entute"]
    correct = stats["gustaj"]
    wrong = stats["malgustaj"]
    pct = (correct / total * 100) if total > 0 else 0.0
    total_time = sum(r.get("tempo_sekundoj", 0) for r in stats["rezultoj"])

    msg = tr_multi(
        f"Recenzo finita! Rezulto: {correct}/{total} ({pct:.0f}%)",
        f"Review complete! Score: {correct}/{total} ({pct:.0f}%)",
        f"Révision terminée ! Score : {correct}/{total} ({pct:.0f}%)",
    )

    panel = Panel(
        f"[bold]{msg}[/]\n\n"
        f"[green]✓ ĝustaj: {correct}[/]\n"
        f"[red]✗ malĝustaj: {wrong}[/]\n"
        f"[dim]tempo: {total_time:.1f}s[/]",
        title="📊",
        border_style="green" if pct >= 70 else "yellow",
    )
    console.print(panel)

    # Message based on performance
    if pct >= 90:
        info(tr_multi(
            "Bonega! Vi estas majstro! 🎉",
            "Excellent! You are a master! 🎉",
            "Excellent ! Vous êtes un maître ! 🎉",
        ))
    elif pct >= 70:
        info(tr_multi(
            "Bone! Daŭre praktiku.",
            "Good! Keep practicing.",
            "Bien ! Continuez à pratiquer.",
        ))
    else:
        info(tr_multi(
            "Vi povas plibonigi. Provu denove!",
            "You can improve. Try again!",
            "Vous pouvez progresser. Réessayez !",
        ))


# ── Persistence ───────────────────────────────────────────────────────────────


def _save_session(mode: str, stats: dict[str, Any]) -> str:
    """Save a review session to the database.

    Args:
        mode: Review mode name (difinoj, tajpu, multobla).
        stats: Stats dict from the review mode.

    Returns:
        Session UUID string.
    """
    db = get_db()
    session_uuid = str(uuid_mod.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    total_time = sum(r.get("tempo_sekundoj", 0) for r in stats["rezultoj"])

    db.execute(
        """INSERT INTO recenzo_sesio (uuid, modo, kreita_je, daŭro_sekundoj,
           entute, ĝustaj, malĝustaj) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            session_uuid,
            mode,
            now,
            total_time,
            stats["entute"],
            stats["gustaj"],
            stats["malgustaj"],
        ),
    )

    for r in stats["rezultoj"]:
        result_uuid = str(uuid_mod.uuid4())
        db.execute(
            """INSERT INTO recenzo_rezulto
               (uuid, sesio_uuid, vorto_uuid, ĝusta, respondo, tempo_sekundoj)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                result_uuid,
                session_uuid,
                r["vorto_uuid"],
                r["gxusta"],
                r.get("respondo", ""),
                r.get("tempo_sekundoj", 0.0),
            ),
        )

    return session_uuid


# ── History subcommands ────────────────────────────────────────────────────────


def _list_sessions(limit: int = 20) -> list[dict[str, Any]]:
    """List recent review sessions.

    Args:
        limit: Max sessions to return.

    Returns:
        List of session dicts.
    """
    db = get_db()
    rows = db.execute(
        """SELECT uuid, modo, kreita_je, daŭro_sekundoj,
           entute, ĝustaj, malĝustaj
           FROM recenzo_sesio
           ORDER BY kreita_je DESC
           LIMIT ?""",
        (limit,),
    )
    return [dict(r) for r in rows]


def _get_session_stats(session_uuid: str) -> dict[str, Any] | None:
    """Get stats for a specific session.

    Args:
        session_uuid: Session UUID.

    Returns:
        Session dict with results list, or None if not found.
    """
    db = get_db()
    row = db.execute_one(
        "SELECT * FROM recenzo_sesio WHERE uuid = ?",
        (session_uuid,),
    )
    if not row:
        return None
    session = dict(row)

    results = db.execute(
        """SELECT r.*, v.teksto FROM recenzo_rezulto r
           LEFT JOIN vorto v ON r.vorto_uuid = v.uuid
           WHERE r.sesio_uuid = ?""",
        (session_uuid,),
    )
    session["rezultoj"] = [dict(r) for r in results]
    return session


def _get_global_stats() -> dict[str, Any]:
    """Get global statistics across all sessions.

    Returns:
        Dict with total_sessions, total_words, total_correct, total_wrong, etc.
    """
    db = get_db()
    row = db.execute_one(
        """SELECT COUNT(*) AS total_sessions,
                  COALESCE(SUM(entute), 0) AS total_words,
                  COALESCE(SUM(ĝustaj), 0) AS total_correct,
                  COALESCE(SUM(malĝustaj), 0) AS total_wrong,
                  COALESCE(SUM(daŭro_sekundoj), 0) AS total_time
           FROM recenzo_sesio""",
    )
    return dict(row) if row else {}


def _delete_session(session_uuid: str) -> bool:
    """Delete a session and its results.

    Args:
        session_uuid: Session UUID.

    Returns:
        True if deleted, False if not found.
    """
    db = get_db()
    with db.transaction() as conn:
        conn.execute("DELETE FROM recenzo_rezulto WHERE sesio_uuid = ?", (session_uuid,))
        cursor = conn.execute("DELETE FROM recenzo_sesio WHERE uuid = ?", (session_uuid,))
    return cursor.rowcount > 0


def _clear_all_history() -> int:
    """Clear all review history.

    Returns:
        Number of deleted sessions.
    """
    db = get_db()
    with db.transaction() as conn:
        conn.execute("DELETE FROM recenzo_rezulto")
        cursor = conn.execute("DELETE FROM recenzo_sesio")
    return cursor.rowcount


# ── JSON field helpers ────────────────────────────────────────────────────────


def _parse_json_field(entry: dict[str, Any], field: str) -> list[str]:
    """Parse a JSON list field from an entry.

    Args:
        entry: Entry dict.
        field: Field name (difinoj, uzoj).

    Returns:
        List of strings.
    """
    raw = entry.get(field) or "[]"
    if isinstance(raw, str):
        try:
            return json.loads(raw) if raw.strip() else []
        except (json.JSONDecodeError, TypeError):
            return []
    return raw or []


__all__ = [
    "_recenzi_difinoj",
    "_recenzi_tajpu",
    "_recenzi_multobla",
    "_celebrate",
    "_save_session",
    "_list_sessions",
    "_get_session_stats",
    "_get_global_stats",
    "_delete_session",
    "_clear_all_history",
]
