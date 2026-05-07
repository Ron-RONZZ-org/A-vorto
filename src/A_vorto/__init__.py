"""A-vorto - personal wordbook."""

# Entry point is A_vorto.cli:app — no re-export needed.
# Removing it breaks a circular import chain that corrupts
# module-level type annotation evaluation (list[str] fails).
__all__: list[str] = []