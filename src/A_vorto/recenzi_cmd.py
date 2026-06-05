"""Interactive review (recenzi) command for A-vorto.

Builds on the same filter logic as `serci` to select entries, then runs
an interactive review session in one of several modes:
- difinoj: show definitions, Enter to advance
- tajpu: show definition, type the word
- multobla: 4-option multiple choice
"""

from __future__ import annotations

import typer

from A import error, info, tr_multi
from A.utils.output import console
from A.utils.interactive import confirm_action

from A_vorto.service import get_service
from A_vorto.search_helpers import _run_search
from A_vorto.recenzi_helpers import (
    _recenzi_difinoj,
    _recenzi_tajpu,
    _recenzi_multobla,
    _celebrate,
    _save_session,
    _list_sessions,
    _get_session_stats,
    _get_global_stats,
    _delete_session,
    _clear_all_history,
)

# ── Main review command ───────────────────────────────────────────────────────


def recenzi(
    teksto: str | None = typer.Argument(
        None,
        help=tr_multi(
            "Text to filter (default: all entries)",
            "Text to filter (default: all entries)",
            "Texte pour filtrer (defaut: toutes les entrees)",
        ),
    ),
    modo: str = typer.Option(
        "difinoj",
        "-m",
        "--modo",
        help=tr_multi(
            "Review mode: difinoj, tajpu, multobla",
            "Review mode: difinoj, tajpu, multobla",
            "Mode de revision: difinoj, tajpu, multobla",
        ),
    ),
    # Filter options (mirrors serci)
    lingvo: str | None = typer.Option(
        None, "-l", "--lingvo",
        help=tr_multi("Filter by language", "Filter by language", "Filtrer par langue"),
    ),
    tipo: str | None = typer.Option(
        None, "-t", "--tipo",
        help=tr_multi("Filter by type", "Filter by type", "Filtrer par type"),
    ),
    temo: str | None = typer.Option(
        None, "--temo",
        help=tr_multi("Filter by theme", "Filter by theme", "Filtrer par theme"),
    ),
    tono: str | None = typer.Option(
        None, "--tono",
        help=tr_multi("Filter by tonality", "Filter by tonality", "Filtrer par tonalite"),
    ),
    autoro: str | None = typer.Option(
        None, "-a", "--autoro",
        help=tr_multi("Filter by author", "Filter by author", "Filtrer par auteur"),
    ),
    verko: str | None = typer.Option(
        None, "-v", "--verko",
        help=tr_multi("Filter by work", "Filter by work", "Filtrer par oeuvre"),
    ),
    nivelo_min: float | None = typer.Option(
        None, "--nivelo-min",
        help=tr_multi("Min lexical level", "Min lexical level", "Niveau min"),
    ),
    nivelo_max: float | None = typer.Option(
        None, "--nivelo-max",
        help=tr_multi("Max lexical level", "Max lexical level", "Niveau max"),
    ),
    dato_de: str | None = typer.Option(
        None, "--dato-de",
        help=tr_multi("Start date YYYY-MM-DD", "Start date YYYY-MM-DD", "Date debut AAAA-MM-JJ"),
    ),
    dato_gis: str | None = typer.Option(
        None, "--dato-gis",
        help=tr_multi("End date YYYY-MM-DD", "End date YYYY-MM-DD", "Date fin AAAA-MM-JJ"),
    ),
    regex: bool = typer.Option(
        False, "-r", "--regex",
        help=tr_multi("Interpret text as regex", "Interpret text as regex", "Regex"),
    ),
    preciza: bool = typer.Option(
        False, "-p", "--preciza",
        help=tr_multi("Disable fuzzy fallback", "Disable fuzzy fallback", "Pas de fuzzy"),
    ),
    limo: int = typer.Option(
        50, "-lo", "--limo",
        help=tr_multi("Max entries (default 50)", "Max entries (default 50)", "Max (defaut 50)"),
    ),
    ordo: str = typer.Option(
        "nivelo", "-o", "--ordo",
        help=tr_multi("Order: nivelo/n, dato/d, inversa-dato/id",
                       "Order: nivelo/n, dato/d, inversa-dato/id",
                       "Ordre: nivelo/n, dato/d, inversa-dato/id"),
    ),
) -> None:
    """Interactive vocabulary review.

    Select entries using the same filters as `serci`, then run an
    interactive review session.

    Modes:
    - difinoj: show definitions + usage examples, advance with Enter
    - tajpu: show definition, type the word
    - multobla: 4-option multiple choice
    """
    valid_modes = ("difinoj", "tajpu", "multobla")
    if modo not in valid_modes:
        error(tr_multi(
            f"Nevalida modo: {modo}. Uzu: {', '.join(valid_modes)}",
            f"Invalid mode: {modo}. Use: {', '.join(valid_modes)}",
            f"Mode invalide: {modo}. Utilisez: {', '.join(valid_modes)}",
        ))
        raise typer.Exit(1)

    entries = _run_search(
        teksto=teksto,
        lingvo=lingvo,
        tipo=tipo,
        temo=temo,
        tono=tono,
        autoro=autoro,
        verko=verko,
        nivelo_min=nivelo_min,
        nivelo_max=nivelo_max,
        dato_de=dato_de,
        dato_gis=dato_gis,
        regex=regex,
        preciza=preciza,
        limo=limo,
        ordo=ordo,
    )

    if not entries:
        info(tr_multi(
            "Neniuj rezultoj por recenzo.",
            "No entries to review.",
            "Aucune entree a reviser.",
        ))
        raise typer.Exit(0)

    info(tr_multi(
        f"Komencas recenzo ({modo}) kun {len(entries)} vortoj...",
        f"Starting review ({modo}) with {len(entries)} words...",
        f"Revision ({modo}) avec {len(entries)} mots...",
    ))

    service = get_service()

    if modo == "difinoj":
        stats = _recenzi_difinoj(entries)
    elif modo == "tajpu":
        stats = _recenzi_tajpu(entries, service)
    elif modo == "multobla":
        stats = _recenzi_multobla(entries, service)
    else:
        raise typer.Exit(1)  # unreachable

    _celebrate(stats)
    session_uuid = _save_session(modo, stats)
    info(tr_multi(
        f"Sesio konservita: {session_uuid[:8]}",
        f"Session saved: {session_uuid[:8]}",
        f"Session sauvegardee: {session_uuid[:8]}",
    ))


# ── History subcommand group ──────────────────────────────────────────────────


historio_app = typer.Typer(name="historio", help=tr_multi(
    "Recenzo-historio",
    "Review history",
    "Historique de revision",
))


@historio_app.command("ls")
def historio_list(
    limo: int = typer.Option(
        20, "--limo", "-l",
        help=tr_multi("Max sessions", "Max sessions", "Max sessions"),
    ),
) -> None:
    """List recent review sessions."""
    sessions = _list_sessions(limit=limo)
    if not sessions:
        info(tr_multi(
            "Neniu recenzo-historio.",
            "No review history.",
            "Aucun historique de revision.",
        ))
        return

    from rich.table import Table
    table = Table()
    table.add_column("UUID", style="cyan", width=10)
    table.add_column("Modo", width=10)
    table.add_column("Dato", width=20)
    table.add_column("Rezulto", width=12)
    table.add_column("Tempo", width=8)
    for s in sessions:
        pct = (s["gustaj"] / s["entute"] * 100) if s["entute"] > 0 else 0
        table.add_row(
            s["uuid"][:8],
            s["modo"],
            str(s.get("kreita_je", ""))[:16],
            f"{s['gustaj']}/{s['entute']} ({pct:.0f}%)",
            f"{s.get('daŭro_sekundoj', 0):.0f}s",
        )
    console.print(table)


@historio_app.command("vidi")
def historio_vidi(
    sesio_uuid: str = typer.Argument(
        ..., help=tr_multi("Session UUID", "Session UUID", "UUID de session"),
    ),
) -> None:
    """View details of a specific review session."""
    session = _get_session_stats(sesio_uuid)
    if not session:
        error(tr_multi(
            f"Sesio ne trovita: {sesio_uuid}",
            f"Session not found: {sesio_uuid}",
            f"Session non trouvee: {sesio_uuid}",
        ))
        raise typer.Exit(1)

    pct = (session["gustaj"] / session["entute"] * 100) if session["entute"] > 0 else 0
    console.print(f"[bold]Sesio:[/] {session['uuid'][:8]}")
    console.print(f"[bold]Modo:[/] {session['modo']}")
    console.print(f"[bold]Dato:[/] {session['kreita_je']}")
    console.print(f"[bold]Rezulto:[/] {session['gustaj']}/{session['entute']} ({pct:.0f}%)")
    console.print(f"[bold]Tempo:[/] {session.get('daŭro_sekundoj', 0):.0f}s")
    console.print()

    results = session.get("rezultoj", [])
    if results:
        from rich.table import Table
        table = Table()
        table.add_column("Vorto", width=20)
        table.add_column("Ĝusta", width=8)
        table.add_column("Respondo", width=20)
        table.add_column("Tempo", width=8)
        for r in results:
            table.add_row(
                str(r.get("teksto", ""))[:18],
                "✓" if r["gxusta"] else "✗",
                str(r.get("respondo", ""))[:18],
                f"{r.get('tempo_sekundoj', 0):.1f}s",
            )
        console.print(table)


@historio_app.command("statistiko")
def historio_statistiko() -> None:
    """Show global statistics across all review sessions."""
    stats = _get_global_stats()
    if not stats or stats.get("total_sessions", 0) == 0:
        info(tr_multi(
            "Neniu recenzo-historio.",
            "No review history.",
            "Aucun historique de revision.",
        ))
        return

    total = stats["total_words"]
    correct = stats["total_correct"]
    wrong = stats["total_wrong"]
    pct = (correct / total * 100) if total > 0 else 0

    console.print("[bold]Tutmonda Statistiko[/]")
    console.print(f"  Sesioj: {stats['total_sessions']}")
    console.print(f"  Vortoj: {total}")
    console.print(f"  Ĝustaj: {correct} ({pct:.0f}%)")
    console.print(f"  Malĝustaj: {wrong}")
    console.print(f"  Tempo: {stats['total_time']:.0f}s")


@historio_app.command("forigi")
def historio_forigi(
    sesio_uuid: str = typer.Argument(
        ..., help=tr_multi("Session UUID", "Session UUID", "UUID de session"),
    ),
) -> None:
    """Delete a specific review session."""
    if not confirm_action(tr_multi(
        f"Ĉu forigi session {sesio_uuid[:8]}?",
        f"Delete session {sesio_uuid[:8]}?",
        f"Supprimer la session {sesio_uuid[:8]}?",
    )):
        info(tr_multi("Nuligita.", "Cancelled.", "Annule."))
        return

    if _delete_session(sesio_uuid):
        info(tr_multi(
            f"Sesio forigita: {sesio_uuid[:8]}",
            f"Session deleted: {sesio_uuid[:8]}",
            f"Session supprimee: {sesio_uuid[:8]}",
        ))
    else:
        error(tr_multi(
            f"Sesio ne trovita: {sesio_uuid[:8]}",
            f"Session not found: {sesio_uuid[:8]}",
            f"Session non trouvee: {sesio_uuid[:8]}",
        ))


@historio_app.command("malplenigi")
def historio_malplenigi() -> None:
    """Clear all review history."""
    if not confirm_action(tr_multi(
        "Ĉu forigi CIOM da recenzo-historio?",
        "Delete ALL review history?",
        "Supprimer TOUT l'historique de revision?",
    ), default=False):
        info(tr_multi("Nuligita.", "Cancelled.", "Annule."))
        return

    count = _clear_all_history()
    info(tr_multi(
        f"Forigis {count} sesio(j)n.",
        f"Deleted {count} session(s).",
        f"{count} session(s) supprimee(s).",
    ))


__all__ = ["recenzi", "historio_app"]
