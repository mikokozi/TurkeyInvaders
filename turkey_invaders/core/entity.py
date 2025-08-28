from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class BaseEntity:
    id: int
    kind: str
    x: int
    y: int
    w: int = 1
    h: int = 1
    vx: float = 0.0
    vy: float = 0.0
    hp: int = 1
    alive: bool = True

    def bbox(self) -> Tuple[int, int, int, int]:
        return self.x, self.y, self.w, self.h

    def update(self, dt: float, world) -> None:  # pragma: no cover - base no-op
        pass

    def on_hit(self, damage: int, source: str) -> None:
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False

    def sprite(self) -> Tuple[str, int | None, bool]:  # char, color_pair, bold
        return "?", None, False

