from __future__ import annotations

from .base import Scene
from .gameover import GameOverScene
from ..core.world import World
from ..entities.player import Player
from ..entities.projectile import Projectile
from ..entities.powerup import PowerUp
from ..systems.collision import resolve_collisions
from ..systems.spawner import Spawner
from ..config import Config


class GameplayScene(Scene):
    """Gameplay with entities, collisions, and a basic spawner."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.world = World()
        self.player: Player | None = None
        self.spawner: Spawner | None = None
        self.score = 0
        self.paused = False
        self.help_open = False
        self._was_paused = False
        self._bomb_flash = 0.0
        self.config = config
        # per-frame movement intent (-1, 0, +1) for dt-based motion
        self._intent_x = 0
        self._intent_y = 0

    def _ensure_initialized(self, w: int, h: int) -> None:
        if self.player is not None:
            return
        self.world.width = w
        self.world.height = h
        self.player = Player(self.world.next_id(), x=w // 2, y=h - 2)
        self.world.player = self.player
        self.world.add(self.player)
        self.spawner = Spawner(self.world)

    def handle_actions(self, actions):
        # Toggle help overlay (pauses game while open)
        if 'help' in actions:
            if not self.help_open:
                self._was_paused = self.paused
                self.paused = True
                self.help_open = True
            else:
                self.help_open = False
                self.paused = self._was_paused
            return
        if 'quit' in actions and self.paused:
            # from pause, quit back to menu
            # Lazy import to avoid circular import with menu -> gameplay
            from .menu import MenuScene  # type: ignore
            self.next_scene = MenuScene(config=self.config)
            return
        if 'pause' in actions:
            self.paused = not self.paused
            return
        if self.paused:
            return
        if self.player is None:
            return
        # Movement: record intent; applied during update(dt)
        ix = 0
        iy = 0
        if 'left' in actions:
            ix -= 1
        if 'right' in actions:
            ix += 1
        if 'up' in actions:
            iy -= 1
        if 'down' in actions:
            iy += 1
        self._intent_x = ix
        self._intent_y = iy
        # Fire
        if 'fire' in actions and self.player.can_fire():
            self.player.did_fire()
            # Fire pattern based on power (0:1, 1:2, >=2:3)
            xs: list[int]
            if self.player.power <= 0:
                xs = [self.player.x]
            elif self.player.power == 1:
                xs = [self.player.x - 1, self.player.x + 1]
            else:
                xs = [self.player.x - 1, self.player.x, self.player.x + 1]
            for x in xs:
                x = max(1, min(self.world.width - 2, x))
                pid = self.world.next_id()
                self.world.add(Projectile(pid, x, self.player.y - 1, owner="player", vy=-18.0))
        # Bomb clears enemy bullets; only consumes a bomb if something was cleared
        if 'bomb' in actions and self.player and getattr(self.player, 'bombs', 0) > 0:
            cleared = 0
            for p in list(self.world.by_kind.get('proj_enemy', [])):
                if p.alive:
                    p.alive = False
                    cleared += 1
            if cleared > 0:
                self.player.bombs -= 1
                self._bomb_flash = 0.6

    def update(self, dt: float) -> None:
        if self.paused:
            return
        if self._bomb_flash > 0:
            self._bomb_flash = max(0.0, self._bomb_flash - dt)
        # Update world bounds may change on resize (handled in render)
        # Apply dt-based movement intent to player
        if self.player is not None:
            self.player.move_intent(self._intent_x, self._intent_y, dt)
        # Reset intent for next frame
        self._intent_x = 0
        self._intent_y = 0
        # Update entities
        for e in list(self.world.entities):
            e.update(dt, self.world)

        # Spawner
        if self.spawner:
            self.spawner.update(dt)

        # Collisions
        resolve_collisions(self.world)

        # Scoring, drops, and cleanup: enemies that died -> score and occasional drops
        for e in list(self.world.by_kind.get("enemy", [])):
            if not e.alive:
                self.score += 10
                # Drops based on config
                rng = self.spawner.rng if self.spawner else None
                roll = rng.random() if rng else 0.0
                p_power = float(self.config.drops.get('power', 0.20))
                p_bomb = float(self.config.drops.get('bomb', 0.05))
                if roll < p_power:
                    kid = self.world.next_id()
                    self.world.add(PowerUp(kid, e.x, e.y, kind='power'))
                elif roll < p_power + p_bomb:
                    kid = self.world.next_id()
                    self.world.add(PowerUp(kid, e.x, e.y, kind='bomb'))
        self.world.remove_dead()

        # Lives / game over
        if self.player and self.player.lives <= 0:
            self.next_scene = GameOverScene(self.score)

    def render(self, r) -> None:
        w, h = r.get_size()
        self.world.width = w
        self.world.height = h
        self._ensure_initialized(w, h)

        # HUD
        wave_id = self.spawner.current_id() if self.spawner else ""
        r.draw_text(1, 0, f"Score: {self.score}", color_pair=1)
        lives = self.player.lives if self.player else 0
        r.draw_text(max(0, w // 2 - 5), 0, f"Wave: {wave_id}", color_pair=1)
        r.draw_text(w - 14, 0, f"Lives: {lives}", color_pair=1)

        # Borders
        r.draw_text(0, 1, "-" * w)
        r.draw_text(0, h - 1, "-" * w)

        # Draw entities
        for e in self.world.entities:
            ch, color, bold = e.sprite()
            r.draw_text(e.x, e.y, ch, color_pair=color, bold=bold)

        # HUD extras
        if self.player:
            r.draw_text(1, 0, f"Score: {self.score}", color_pair=1)
            r.draw_text(w - 30, 0, f"Power: {self.player.power}", color_pair=1)
            r.draw_text(w - 16, 0, f"Bombs: {getattr(self.player, 'bombs', 0)}", color_pair=1)

        # Bomb flash overlay
        if self._bomb_flash > 0:
            msg = "BOMB!"
            r.draw_text(max(0, w // 2 - len(msg) // 2), max(1, h // 2 - 1), msg, color_pair=1, bold=True)

        # Pause overlay
        if self.paused and not self.help_open:
            msg = "Paused (P resume, Q menu, Esc exit)"
            r.draw_text(max(0, w // 2 - len(msg) // 2), h // 2, msg, color_pair=1, bold=True)

        # Help overlay
        if self.help_open:
            lines = [
                "Controls",
                "- Move: Arrows or WASD",
                "- Fire: Space",
                "- Bomb: X (clears bullets)",
                "- Pause/Help: P / H",
                "- Back to Menu: Q (while paused)",
                "- Exit Game: Esc (with confirm)",
                "",
                "Tips",
                "- Grab P to power up shots",
                "- Grab B to add a bomb",
                "- Bombs clear enemy bullets",
                "",
                "Press H to close help.",
            ]
            box_w = max(len(s) for s in lines) + 4
            box_h = len(lines) + 2
            x0 = max(0, w // 2 - box_w // 2)
            y0 = max(1, h // 2 - box_h // 2)
            r.draw_text(x0, y0, "+" + "-" * (box_w - 2) + "+", color_pair=1)
            for i, s in enumerate(lines, start=1):
                r.draw_text(x0, y0 + i, "| " + s.ljust(box_w - 4) + " |", color_pair=1)
            r.draw_text(x0, y0 + box_h - 1, "+" + "-" * (box_w - 2) + "+", color_pair=1)
