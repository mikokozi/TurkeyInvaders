from __future__ import annotations

import math
import random
from typing import Tuple

from ..core.entity import BaseEntity
from .projectile import Projectile


class Enemy(BaseEntity):
    def __init__(self, id_: int, x: int, y: int, hp: int = 1) -> None:
        super().__init__(id=id_, kind="enemy", x=x, y=y, w=1, h=1, hp=hp)

    def sprite(self) -> Tuple[str, int | None, bool]:
        return "U", None, False


class GruntEnemy(Enemy):
    def __init__(self, id_: int, x: int, y: int, speed: float = 2.0) -> None:
        super().__init__(id_, x, y, hp=1)
        self.speed = speed
        self.dir = 1
        self._ax = 0.0

    def update(self, dt: float, world) -> None:
        # Horizontal sweep bounce within borders, step down occasionally
        self._ax += self.speed * dt
        while self._ax >= 1.0:
            self._ax -= 1.0
            self.x += self.dir
        if self.x <= 1:
            self.x = 1
            self.dir = 1
            self.y += 1
        elif self.x >= world.width - 2:
            self.x = world.width - 2
            self.dir = -1
            self.y += 1
        if self.y >= world.height - 2:
            # Reached player zone
            world.player.on_player_hit()
            self.alive = False


class DiveEnemy(Enemy):
    def __init__(self, id_: int, x: int, y: int, speed: float = 3.0) -> None:
        super().__init__(id_, x, y, hp=1)
        self.speed = speed
        self.t = 0.0
        self._ay = 0.0

    def update(self, dt: float, world) -> None:
        self.t += dt
        # Curve roughly toward player X using a sine wobble
        target_x = world.player.x
        dx = 1 if target_x > self.x else -1 if target_x < self.x else 0
        self.x += dx
        self._ay += self.speed * dt
        while self._ay >= 1.0:
            self._ay -= 1.0
            self.y += 1
        self.x += int(round(1.2 * math.sin(self.t * 4.0)))
        self.x = max(1, min(world.width - 2, self.x))
        if self.y >= world.height - 2:
            world.player.on_player_hit()
            self.alive = False


class ShooterEnemy(Enemy):
    def __init__(self, id_: int, x: int, y: int, speed: float = 2.0, fire_interval: float = 2.0) -> None:
        super().__init__(id_, x, y, hp=1)
        self.speed = speed
        self.dir = random.choice([-1, 1])
        self.fire_interval = fire_interval
        self._cooldown = fire_interval
        self._ax = 0.0
        self._ay = 0.0

    def update(self, dt: float, world) -> None:
        # Horizontal patrol
        self._ax += self.speed * dt
        while self._ax >= 1.0:
            self._ax -= 1.0
            self.x += self.dir
        if self.x <= 1:
            self.x = 1
            self.dir *= -1
        elif self.x >= world.width - 2:
            self.x = world.width - 2
            self.dir *= -1

        # Shooting
        self._cooldown -= dt
        if self._cooldown <= 0:
            self._cooldown = self.fire_interval
            # Fire straight down toward player area
            pid = world.next_id()
            world.add(Projectile(pid, self.x, self.y + 1, owner="enemy", vy=+1))

        # Advance slowly downward
        self._ay += 0.5 * dt
        while self._ay >= 1.0:
            self._ay -= 1.0
            self.y += 1
        if self.y >= world.height - 2:
            world.player.on_player_hit()
            self.alive = False
