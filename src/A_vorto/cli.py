"""CLI for vorto command."""

from __future__ import annotations

import typer

from A import info, tr
from A.console import console

app = typer.Typer(
    name="vorto",
    help=tr(
        "Mia Vorto — persona vortaro-mikroapo.",
        "Mia Vorto — personal wordbook microapp.",
        "Mia Vorto — microapplication de vocabulaire personnel.",
    ),
    no_args_is_help=False,
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help", "--helpo"]},
)


@app.command()
def ls() -> None:
    """List all word entries."""
    info("[dim]TODO: implement list[/dim]")


@app.command()
def vidi(uuid: str) -> None:
    """View a word entry by UUID."""
    info(f"[dim]TODO: implement vidi {uuid}[/dim]")


__all__ = ["app"]