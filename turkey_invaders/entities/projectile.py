from __future__ import annotations

from typing import Tuple

from ..core.entity import BaseEntity


class Projectile(BaseEntity):
    def __init__(self, id_: int, x: int, y: int, owner: str, vy: float) -> None:
        super().__init__(id=id_, kind="proj_" + owner, x=x, y=y, w=1, h=1, hp=1)
        self.owner = owner  # 'player' or 'enemy'
        self.vy = vy  # cells per second (float)
        self._ay = 0.0
        self.damage = 1

    def update(self, dt: float, world) -> None:
        self._ay += self.vy * dt
        # Move in whole-cell steps using accumulator
        while self._ay <= -1.0:
            self._ay += 1.0
            self.y -= 1
        while self._ay >= 1.0:
            self._ay -= 1.0
            self.y += 1
        # Remove if out of bounds
        if self.y < 1 or self.y >= world.height - 1:
            self.alive = False

    def sprite(self) -> Tuple[str, int | None, bool]:
        return ("|" if self.owner == "player" else "!"), None, False
