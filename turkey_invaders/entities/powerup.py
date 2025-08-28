from __future__ import annotations

from typing import Tuple

from ..core.entity import BaseEntity


class PowerUp(BaseEntity):
    def __init__(self, id_: int, x: int, y: int, kind: str) -> None:
        super().__init__(id=id_, kind=f"powerup_{kind}", x=x, y=y, w=1, h=1, hp=1)
        self.type = kind  # 'power' or 'bomb'
        self._ay = 0.0

    def update(self, dt: float, world) -> None:
        # Fall at 4 cells/sec using accumulator
        self._ay += 4.0 * dt
        while self._ay >= 1.0:
            self._ay -= 1.0
            self.y += 1
            if self.y >= world.height - 1:
                self.alive = False

    def sprite(self) -> Tuple[str, int | None, bool]:
        ch = "P" if self.type == "power" else "B"
        return ch, 1, True

