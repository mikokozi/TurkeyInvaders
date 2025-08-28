from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "fps": 60,
    "scale": 1,
    "controls": {
        "left": ["LEFT", "a"],
        "right": ["RIGHT", "d"],
        "up": ["UP", "w"],
        "down": ["DOWN", "s"],
        "fire": ["SPACE"],
        "bomb": ["x"],
        "pause": ["p"],
        "quit": ["q"],
        "exit": ["ESC"],
        "start": ["ENTER", "SPACE"],
        "options": ["o"],
        "help": ["h"],
        "yes": ["y", "Y"],
        "no": ["n", "N"],
    },
    "drops": {
        "power": 0.20,
        "bomb": 0.05
    },
}


def _cfg_dir() -> str:
    return os.path.join(os.path.expanduser("~"), ".config", "turkey_invaders")


def _cfg_path() -> str:
    return os.path.join(_cfg_dir(), "config.json")


@dataclass
class Config:
    data: Dict[str, Any] = field(default_factory=lambda: json.loads(json.dumps(DEFAULT_CONFIG)))
    path: str = field(default_factory=_cfg_path)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    @property
    def controls(self) -> Dict[str, Any]:
        return self.data.setdefault("controls", {})

    @property
    def drops(self) -> Dict[str, float]:
        return self.data.setdefault("drops", {})

    @property
    def fps(self) -> int:
        return int(self.data.get("fps", 60))

    @property
    def scale(self) -> int:
        try:
            s = int(self.data.get("scale", 1))
        except Exception:
            s = 1
        return max(1, min(4, s))

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)


def load_config() -> Config:
    cfg = Config()
    path = cfg.path
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                user = json.load(f)
            # Merge shallowly
            merged = json.loads(json.dumps(DEFAULT_CONFIG))
            def merge(a, b):
                for k, v in b.items():
                    if isinstance(v, dict) and isinstance(a.get(k), dict):
                        a[k].update(v)
                    else:
                        a[k] = v
                return a
            merged = merge(merged, user)
            cfg.data = merged
    except Exception:
        pass
    return cfg
