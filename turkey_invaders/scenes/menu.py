from __future__ import annotations

from .base import Scene
from .gameplay import GameplayScene
from .options import OptionsScene
from ..config import Config


TITLE = "Turkey Invaders"


class MenuScene(Scene):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.show_help = False

    def handle_actions(self, actions):
        # If help is open, only toggle help/quit
        if self.show_help:
            if 'help' in actions or 'start' in actions or 'pause' in actions:
                self.show_help = False
            if 'quit' in actions:
                self.exit_program = True
            return

        if 'quit' in actions:
            self.exit_program = True
        if 'start' in actions or 'fire' in actions:
            self.next_scene = GameplayScene(config=self.config)
        if 'options' in actions:
            # Options runs and returns to menu on save/quit; we recreate menu on return
            self.next_scene = OptionsScene(self.config)
        if 'help' in actions:
            self.show_help = True

    def render(self, r) -> None:
        w, h = r.get_size()
        cx = max(0, w // 2 - len(TITLE) // 2)
        r.draw_text(cx, h // 2 - 1, TITLE, color_pair=1, bold=True)
        r.draw_text(max(0, w // 2 - 12), h // 2 + 1, "Enter/Space: Start", color_pair=1)
        r.draw_text(max(0, w // 2 - 8), h // 2 + 2, "O: Options  H: Help", color_pair=1)
        r.draw_text(max(0, w // 2 - 12), h // 2 + 3, "Q: Back   Esc: Exit", color_pair=1)

        # Quick controls help
        r.draw_text(max(0, w // 2 - 12), h // 2 + 5, "Move: Arrows or WASD", color_pair=1)
        r.draw_text(max(0, w // 2 - 8),  h // 2 + 6, "Fire: Space", color_pair=1)
        r.draw_text(max(0, w // 2 - 8),  h // 2 + 7, "Bomb: X", color_pair=1)
        r.draw_text(max(0, w // 2 - 12), h // 2 + 8, "Pause: P   Menu: Q   Exit: Esc", color_pair=1)

        # Help overlay
        if self.show_help:
            lines = [
                "Controls",
                "- Move: Arrows or WASD",
                "- Fire: Space",
                "- Bomb: X (clears bullets)",
                "- Pause: P",
                "- Options: O",
                "- Menu: Q   Exit: Esc",
                "",
                "Tips",
                "- Collect P (power) to widen shots.",
                "- Collect B (bomb) to gain bombs.",
                "- Use bombs to clear dense patterns.",
                "",
                "Press H to close help.",
            ]
            box_w = max(len(s) for s in lines) + 4
            box_h = len(lines) + 2
            x0 = max(0, w // 2 - box_w // 2)
            y0 = max(0, h // 2 - box_h // 2)
            # simple border
            r.draw_text(x0, y0, "+" + "-" * (box_w - 2) + "+", color_pair=1)
            for i, s in enumerate(lines, start=1):
                r.draw_text(x0, y0 + i, "| " + s.ljust(box_w - 4) + " |", color_pair=1)
            r.draw_text(x0, y0 + box_h - 1, "+" + "-" * (box_w - 2) + "+", color_pair=1)
