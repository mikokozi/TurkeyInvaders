"""Input system mapping curses keys to actions.

Produces a set of high-level actions per frame for scenes to consume.
Configurable via controls mapping.
"""
from __future__ import annotations

import curses
from typing import List


KEY_NAME_MAP = {
    # Arrows and special
    "LEFT": lambda: curses.KEY_LEFT,
    "RIGHT": lambda: curses.KEY_RIGHT,
    "UP": lambda: curses.KEY_UP,
    "DOWN": lambda: curses.KEY_DOWN,
    "SPACE": lambda: ord(' '),
    "ENTER": lambda: 10,  # also 13
    "ESC": lambda: 27,
}


def _names_to_codes(names: List[str]) -> List[int]:
    codes: List[int] = []
    for name in names:
        key = name
        if not key:
            continue
        key = key.strip()
        if key.upper() in KEY_NAME_MAP:
            try:
                codes.append(int(KEY_NAME_MAP[key.upper()]()))
                if key.upper() == "ENTER":
                    codes.append(13)
            except Exception:
                pass
        elif len(key) == 1:
            # Add both cases for convenience (e.g., 'x' and 'X')
            ch = key
            codes.append(ord(ch))
            if ch.swapcase() != ch:
                codes.append(ord(ch.swapcase()))
        else:
            # fallback: try curses constant by name
            try:
                codes.append(int(getattr(curses, key)))
            except Exception:
                pass
    return codes


class Input:
    def __init__(self, stdscr, controls: dict | None = None) -> None:
        self.stdscr = stdscr
        self._bindings = self._compile_bindings(controls or {})

    def _compile_bindings(self, controls: dict) -> dict[int, str]:
        bindings: dict[int, str] = {}
        for action, names in controls.items():
            codes = _names_to_codes(list(names)) if isinstance(names, list) else _names_to_codes([str(names)])
            for code in codes:
                # Do not override earlier bindings; this lets 'fire' keep SPACE
                # even if a later action (like 'start') also binds SPACE.
                bindings.setdefault(code, action)
        # Always include some sane defaults
        for code, action in (
            (ord('Q'), 'quit'), (ord('q'), 'quit'),
            (ord('P'), 'pause'), (ord('p'), 'pause'),
        ):
            bindings.setdefault(code, action)
        return bindings

    def poll(self) -> List[str]:
        actions: List[str] = []
        while True:
            ch = self.stdscr.getch()
            if ch == -1:
                break
            # Lookup by bindings
            action = self._bindings.get(ch)
            if action:
                actions.append(action)
        return actions
