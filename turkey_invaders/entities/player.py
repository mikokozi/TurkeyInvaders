from __future__ import annotations

from typing import Tuple

from ..core.entity import BaseEntity
from ..audio import sfx


class Player(BaseEntity):
    def __init__(self, id_: int, x: int, y: int) -> None:
        super().__init__(id=id_, kind="player", x=x, y=y, w=1, h=1, hp=1)
        self.speed = 20.0  # cells per second
        self.fire_cd = 0.16
        self._cooldown = 0.0
        self.power = 0
        self.lives = 3
        self.invuln = 0.0
        self.bombs = 1
        # sub-cell movement accumulators for dt-based movement
        self._mx = 0.0
        self._my = 0.0

    def update(self, dt: float, world) -> None:
        if self._cooldown > 0:
            self._cooldown -= dt
        if self.invuln > 0:
            self.invuln -= dt

        # Clamp to playfield width
        w, h = world.width, world.height
        self.x = max(1, min(max(1, w - 2), self.x))
        self.y = max(1, min(max(1, h - 2), self.y))

        # Apply sub-cell movement accumulators into whole-cell steps
        while self._mx <= -1.0:
            self._mx += 1.0
            self.x -= 1
        while self._mx >= 1.0:
            self._mx -= 1.0
            self.x += 1
        while self._my <= -1.0:
            self._my += 1.0
            self.y -= 1
        while self._my >= 1.0:
            self._my -= 1.0
            self.y += 1
        # Re-clamp in case of boundary crossing
        self.x = max(1, min(max(1, w - 2), self.x))
        self.y = max(1, min(max(1, h - 2), self.y))

    def move_intent(self, ix: int, iy: int, dt: float) -> None:
        """Accumulate movement intent scaled by speed and dt.

        ix/iy: -1,0,1 directional intents for this frame.
        """
        if ix:
            self._mx += float(ix) * self.speed * dt
        if iy:
            self._my += float(iy) * self.speed * dt

    def can_fire(self) -> bool:
        return self._cooldown <= 0.0

    def did_fire(self) -> None:
        self._cooldown = self.fire_cd

    def on_player_hit(self) -> None:
        if self.invuln > 0:
            return
        self.lives -= 1
        self.invuln = 1.5
        if self.power > 0:
            self.power -= 1
        sfx('hit')

    def sprite(self) -> Tuple[str, int | None, bool]:
        # Blink while invulnerable
        if self.invuln > 0:
            return "^", 2, False
        return "^", 2, True
