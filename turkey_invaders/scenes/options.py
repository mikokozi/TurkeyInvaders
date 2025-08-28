from __future__ import annotations

from .base import Scene
from ..config import Config


class OptionsScene(Scene):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.cursor = 0  # 0: FPS, 1: Power drop, 2: Bomb drop
        self.show_help = False

    def handle_actions(self, actions):
        # If help overlay is open, allow closing it with H/Enter/P
        if self.show_help:
            if 'help' in actions or 'start' in actions or 'pause' in actions:
                self.show_help = False
            if 'quit' in actions:
                from .menu import MenuScene
                self.next_scene = MenuScene(config=self.config)
            return

        if 'quit' in actions:
            # Do not save on quit; return to menu
            from .menu import MenuScene
            self.next_scene = MenuScene(config=self.config)
            return
        if 'help' in actions:
            self.show_help = True
            return
        if 'up' in actions:
            self.cursor = (self.cursor - 1) % 3
        if 'down' in actions:
            self.cursor = (self.cursor + 1) % 3
        if 'left' in actions:
            self._adjust(-1)
        if 'right' in actions:
            self._adjust(+1)
        if 'start' in actions:
            # save and return to menu
            from .menu import MenuScene
            self.config.save()
            self.next_scene = MenuScene(config=self.config)

    def _adjust(self, delta: int) -> None:
        if self.cursor == 0:
            fps = max(30, min(120, int(self.config.fps + (10 * delta))))
            self.config.set('fps', fps)
        elif self.cursor == 1:
            p = max(0.0, min(1.0, float(self.config.drops.get('power', 0.2) + 0.05 * delta)))
            self.config.drops['power'] = p
        elif self.cursor == 2:
            p = max(0.0, min(1.0, float(self.config.drops.get('bomb', 0.05) + 0.05 * delta)))
            self.config.drops['bomb'] = p

    def render(self, r) -> None:
        w, h = r.get_size()
        cx = max(0, w // 2 - 10)
        y = h // 2 - 4
        r.draw_text(cx, y, "Options", color_pair=1, bold=True)
        y += 2
        entries = [
            ("FPS", f"{self.config.fps}"),
            ("Power Drop", f"{self.config.drops.get('power', 0.2):.2f}"),
            ("Bomb Drop", f"{self.config.drops.get('bomb', 0.05):.2f}"),
        ]
        for idx, (label, value) in enumerate(entries):
            sel = "> " if idx == self.cursor else "  "
            r.draw_text(cx, y, f"{sel}{label}: {value}")
            y += 1
        y += 1
        r.draw_text(cx, y, "Left/Right: Adjust   Up/Down: Select")
        r.draw_text(cx, y + 1, "Enter: Save & Back   Q: Quit   Esc: Exit   H: Help")

        # Help overlay
        if self.show_help:
            lines = [
                "Options Help",
                "- Up/Down: choose a setting",
                "- Left/Right: change value",
                "- Enter: save and return",
                "- Q: cancel and return   Esc: exit game",
                "",
                "Game Controls",
                "- Move: Arrows or WASD",
                "- Fire: Space",
                "- Bomb: X (clears bullets)",
                "- Pause/Help: P / H",
                "",
                "Press H to close help.",
            ]
            box_w = max(len(s) for s in lines) + 4
            box_h = len(lines) + 2
            x0 = max(0, w // 2 - box_w // 2)
            y0 = max(0, h // 2 - box_h // 2)
            r.draw_text(x0, y0, "+" + "-" * (box_w - 2) + "+", color_pair=1)
            for i, s in enumerate(lines, start=1):
                r.draw_text(x0, y0 + i, "| " + s.ljust(box_w - 4) + " |", color_pair=1)
            r.draw_text(x0, y0 + box_h - 1, "+" + "-" * (box_w - 2) + "+", color_pair=1)
