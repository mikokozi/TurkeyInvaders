from __future__ import annotations

from typing import Dict, List
from .entity import BaseEntity


class World:
    def __init__(self) -> None:
        self.entities: List[BaseEntity] = []
        self.by_kind: Dict[str, List[BaseEntity]] = {}
        self._next_id = 1
        # Initialize common ad-hoc attributes used by systems/scenes
        self.player = None  # set by scene when player is created
        self.width = 0
        self.height = 0

    def next_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    def add(self, e: BaseEntity) -> None:
        self.entities.append(e)
        self.by_kind.setdefault(e.kind, []).append(e)

    def remove_dead(self) -> None:
        self.entities = [e for e in self.entities if e.alive]
        self.by_kind = {}
        for e in self.entities:
            self.by_kind.setdefault(e.kind, []).append(e)

    def width_height(self) -> tuple[int, int]:
        # Provided by scene/renderer; stored ad-hoc as attributes for simplicity
        return getattr(self, "width", 0), getattr(self, "height", 0)
