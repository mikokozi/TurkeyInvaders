from __future__ import annotations

from typing import Iterable


class Scene:
    """Base scene interface.

    Subclasses set `next_scene` to transition, or `exit_program = True` to quit.
    """

    def __init__(self) -> None:
        self.next_scene = None
        self.exit_program = False

    def handle_actions(self, actions: Iterable[str]) -> None:  # noqa: D401
        """Consume per-frame action list."""
        pass

    def update(self, dt: float) -> None:  # noqa: D401
        """Advance scene state by dt seconds."""
        pass

    def render(self, r) -> None:  # noqa: D401
        """Draw scene via renderer r."""
        pass
