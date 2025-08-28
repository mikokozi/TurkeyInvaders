from __future__ import annotations

from typing import List


class StdoutRenderer:
    """Simple text renderer for headless mode.

    Collects draw_text calls into a char buffer and prints on end_frame.
    Color/bold hints are ignored.
    """

    def __init__(self, *, width: int = 80, height: int = 24, scale: int = 1) -> None:
        # width/height are logical cells; scale inflates the printed buffer
        self.width = max(20, width)
        self.height = max(10, height)
        self.scale = max(1, int(scale))
        self._buffer: List[List[str]] = []

    def get_size(self) -> tuple[int, int]:
        return self.width, self.height

    def begin_frame(self) -> None:
        self._buffer = [[" "] * self.width for _ in range(self.height)]

    def draw_text(self, x: int, y: int, text: str, *, color_pair: int | None = None, bold: bool = False) -> None:  # noqa: ARG002
        if y < 0 or y >= self.height:
            return
        if x < 0:
            # clip left
            text = text[-x:]
            x = 0
        if x >= self.width:
            return
        max_len = self.width - x
        text = text[:max_len]
        row = self._buffer[y]
        for i, ch in enumerate(text):
            row[x + i] = ch

    def end_frame(self) -> None:
        # Inflate buffer by scale
        if self.scale > 1:
            inflated: List[str] = []
            for row in self._buffer:
                line = "".join(ch * self.scale for ch in row).rstrip()
                for _ in range(self.scale):
                    inflated.append(line)
            lines = inflated
        else:
            lines = ["".join(row).rstrip() for row in self._buffer]
        while lines and not lines[-1]:
            lines.pop()
        print("\n".join(lines))
        print("\n---")
