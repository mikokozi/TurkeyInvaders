from __future__ import annotations

from .base import Scene


class GameOverScene(Scene):
    def __init__(self, score: int) -> None:
        super().__init__()
        self.score = score

    def handle_actions(self, actions):
        if 'quit' in actions or 'start' in actions or 'fire' in actions:
            self.exit_program = True

    def render(self, r) -> None:
        w, h = r.get_size()
        title = "Game Over"
        r.draw_text(max(0, w // 2 - len(title) // 2), h // 2 - 1, title, color_pair=3, bold=True)
        msg = f"Score: {self.score}"
        r.draw_text(max(0, w // 2 - len(msg) // 2), h // 2 + 0, msg)
        r.draw_text(max(0, w // 2 - 11), h // 2 + 2, "Press Q to exit")
