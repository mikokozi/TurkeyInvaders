from __future__ import annotations

from typing import Iterable, List, Tuple

from ..core.entity import BaseEntity


def aabb_intersect(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)


def resolve_collisions(world) -> None:
    """Simple collision resolution for v0.1.

    - Player projectiles vs enemies -> damage/destroy, score increment handled in scene.
    - Enemy contact vs player -> player hit.
    - Enemy projectiles vs player -> player hit.
    """
    player = world.player
    if player is None:
        return

    player_bb = player.bbox()

    # Enemy vs player contact
    for e in list(world.by_kind.get("enemy", [])):
        if aabb_intersect(e.bbox(), player_bb):
            player.on_player_hit()
            e.alive = False

    # Enemy projectile vs player
    for p in list(world.by_kind.get("proj_enemy", [])):
        if aabb_intersect(p.bbox(), player_bb):
            player.on_player_hit()
            p.alive = False

    # Player projectiles vs enemies
    for p in list(world.by_kind.get("proj_player", [])):
        pbb = p.bbox()
        for e in list(world.by_kind.get("enemy", [])):
            if aabb_intersect(pbb, e.bbox()):
                e.on_hit(p.damage, source="player")
                p.alive = False
                break

    # Player vs power-ups
    for item in list(world.entities):
        if not item.kind.startswith("powerup_"):
            continue
        if aabb_intersect(player_bb, item.bbox()):
            if item.kind == "powerup_power":
                world.player.power = min(5, world.player.power + 1)
            elif item.kind == "powerup_bomb":
                world.player.bombs = min(9, getattr(world.player, 'bombs', 0) + 1)
            item.alive = False
