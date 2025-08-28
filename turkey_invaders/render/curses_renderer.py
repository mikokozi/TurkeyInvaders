from __future__ import annotations

import curses
from typing import Tuple


class CursesRenderer:
    """Minimal curses-based renderer with a simple API."""

    def __init__(self, stdscr) -> None:
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
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
        self.height, self.width = self.stdscr.getmaxyx()

    def end_frame(self) -> None:
        try:
            self.stdscr.noutrefresh()
            curses.doupdate()
        except Exception:
            self.stdscr.refresh()

    def get_size(self) -> Tuple[int, int]:
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
        try:
            self.stdscr.addnstr(y, x, text, max(0, self.width - x), attr)
        except Exception:
            pass
