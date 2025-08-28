from __future__ import annotations

import curses
from typing import Tuple


class CursesRenderer:
    """Minimal curses-based renderer with a simple API."""

    def __init__(self, stdscr, *, scale: int = 1) -> None:
        self.stdscr = stdscr
        self.term_height, self.term_width = stdscr.getmaxyx()
        self.scale = max(1, int(scale))
        self.height = max(1, self.term_height // self.scale)
        self.width = max(1, self.term_width // self.scale)
        curses.start_color()
        curses.use_default_colors()
        try:
            curses.init_pair(1, curses.COLOR_YELLOW, -1)  # HUD/Title
            curses.init_pair(2, curses.COLOR_CYAN, -1)    # Player
            curses.init_pair(3, curses.COLOR_RED, -1)     # Warning
        except Exception:
            pass

    def begin_frame(self) -> None:
        self.stdscr.erase()
        self.term_height, self.term_width = self.stdscr.getmaxyx()
        self.height = max(1, self.term_height // self.scale)
        self.width = max(1, self.term_width // self.scale)

    def end_frame(self) -> None:
        try:
            self.stdscr.noutrefresh()
            curses.doupdate()
        except Exception:
            self.stdscr.refresh()

    def get_size(self) -> Tuple[int, int]:
        # Return logical size, scaled down from terminal
        return self.width, self.height

    def draw_text(self, x: int, y: int, text: str, color_pair: int | None = None, bold: bool = False) -> None:
        if y < 0 or y >= self.height:
            return
        if x < 0:
            text = text[-x:]
            x = 0
        if x >= self.width:
            return
        attr = curses.color_pair(color_pair) if color_pair else 0
        if bold:
            attr |= curses.A_BOLD
        # Scale horizontally by repeating characters
        if self.scale > 1:
            text = "".join(ch * self.scale for ch in text)
        # Map logical coordinates to terminal coordinates
        ty = y * self.scale
        tx = x * self.scale
        # Draw repeated vertically for vertical scale
        for i in range(self.scale):
            row_y = ty + i
            if 0 <= row_y < self.term_height:
                try:
                    self.stdscr.addnstr(row_y, tx, text, max(0, self.term_width - tx), attr)
                except Exception:
                    pass
