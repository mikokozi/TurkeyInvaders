from __future__ import annotations

import json
import os
import random
from typing import Any, Dict, List, Optional

from ..core.world import World
from ..entities.enemy import GruntEnemy, DiveEnemy, ShooterEnemy


class Spawner:
    def __init__(self, world: World, waves_path: Optional[str] = None) -> None:
        self.world = world
        self.waves: List[Dict[str, Any]] = []
        self.wave_index = 0
        self.timer = 0.0
        self.spawn_accum = 0.0
        self.rng = random.Random(1337)
        self._spawned_once = False  # for one-shot formation waves
        if waves_path is None:
            waves_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "waves.json")
        self._load_waves(waves_path)

    def _load_waves(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {"seed": 1337, "waves": [{"id": "wave1", "type": "formation", "rows": 1, "cols": 6, "speed": 2.0}]}
        self.rng = random.Random(int(data.get("seed", 1337)))
        self.waves = list(data.get("waves", []))
        if not self.waves:
            self.waves = [{"id": "wave1", "type": "formation", "rows": 1, "cols": 6, "speed": 2.0}]

    def current_id(self) -> str:
        if 0 <= self.wave_index < len(self.waves):
            return str(self.waves[self.wave_index].get("id", f"wave{self.wave_index+1}"))
        return ""

    def update(self, dt: float) -> None:
        if self.wave_index >= len(self.waves):
            return
        wave = self.waves[self.wave_index]
        self.timer += dt

        if wave.get("type") == "formation":
            # Instant spawn once at start of wave
            if not self._spawned_once:
                self._spawn_formation(wave)
                self._spawned_once = True
        else:
            rate = float(wave.get("spawn_rate", 1.0))
            count = int(wave.get("count", 10))
            spawned = len([e for e in self.world.by_kind.get("enemy", []) if getattr(e, "_wave", None) == self.wave_index])
            self.spawn_accum += rate * dt
            while self.spawn_accum >= 1.0 and spawned < count:
                self.spawn_accum -= 1.0
                self._spawn_one(wave)
                spawned += 1

        # Check wave completion
        if not self.world.by_kind.get("enemy", []) and self.timer > 0.1:
            # advance to next wave
            self.wave_index += 1
            self.timer = 0.0
            self.spawn_accum = 0.0
            self._spawned_once = False

    # --- spawn helpers ---
    def _spawn_formation(self, wave: Dict[str, Any]) -> None:
        rows = int(wave.get("rows", 1))
        cols = int(wave.get("cols", max(3, (self.world.width - 2) // 4)))
        speed = float(wave.get("speed", 2.0))
        start_y = 2
        spacing_x = max(2, (self.world.width - 2) // (cols + 1))
        for r in range(rows):
            for c in range(cols):
                x = 1 + (c + 1) * spacing_x
                y = start_y + r * 2
                eid = self.world.next_id()
                e = GruntEnemy(eid, x, y, speed=speed)
                setattr(e, "_wave", self.wave_index)
                self.world.add(e)

    def _spawn_one(self, wave: Dict[str, Any]) -> None:
        w = self.world.width
        x = self.rng.randint(1, max(1, w - 2))
        etype = wave.get("type", "dive")
        if etype == "dive":
            eid = self.world.next_id()
            e = DiveEnemy(eid, x, 1, speed=float(wave.get("speed", 3.0)))
        elif etype == "mixed":
            patterns = wave.get("patterns", [{"type": "grunt", "weight": 3}, {"type": "shooter", "weight": 1}])
            choice = self._weighted_choice(patterns)
            if choice == "shooter":
                eid = self.world.next_id()
                e = ShooterEnemy(eid, x, 1, speed=float(wave.get("speed", 2.0)), fire_interval=float(wave.get("fire_interval", 2.0)))
            else:
                eid = self.world.next_id()
                e = GruntEnemy(eid, x, 1, speed=float(wave.get("speed", 2.0)))
        else:  # default grunt
            eid = self.world.next_id()
            e = GruntEnemy(eid, x, 1, speed=float(wave.get("speed", 2.0)))
        setattr(e, "_wave", self.wave_index)
        self.world.add(e)

    def _weighted_choice(self, items: List[Dict[str, Any]]) -> str:
        total = sum(int(i.get("weight", 1)) for i in items)
        pick = self.rng.uniform(0, total)
        upto = 0.0
        for i in items:
            w = int(i.get("weight", 1))
            if upto + w >= pick:
                return str(i.get("type", "grunt"))
            upto += w
        return str(items[-1].get("type", "grunt"))
