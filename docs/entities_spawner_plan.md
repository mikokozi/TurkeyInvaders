# Turkey Invaders — Entities & Spawner Implementation Plan

## Objectives
- Introduce a real entity model for player, enemies, and projectiles.
- Add a basic, data-driven spawner system that reads wave definitions and schedules spawns deterministically.
- Replace ad-hoc lists in `gameplay.py` with entities + systems wired via the scene.

## Deliverables (v0.1 scope)
- `core/entity.py`: Base class and utilities for entities.
- `entities/player.py`, `entities/enemy.py`, `entities/projectile.py` (minimal versions).
- `systems/collision.py`: AABB grid-based collision checks.
- `systems/spawner.py`: Interprets wave spec (initially inline, then `data/waves.json`).
- `data/waves.json`: 4–6 simple waves (formation, dive, shooter mix) with defaults.
- Scene integration: `gameplay.py` uses entities, collisions, and spawner.
- Tests: collision basics, spawner determinism (seeded).

## High-Level Design

### Entity Base
- Fields: `id`, `kind`, `x`, `y`, `w`, `h`, `vx`, `vy`, `hp`, `alive`.
- Methods:
  - `update(dt, world)`: movement, timers, AI.
  - `bbox() -> (x, y, w, h)`: for collision system.
  - `on_hit(damage, source)`: reduce HP, set `alive=False` if dead.
  - `sprite() -> (char, color_pair, bold)`: rendering hint (ASCII only in v0.1).

### Player
- Fields: `speed=12 cps`, `fire_cooldown=0.16s`, `power_level=0..5`, `lives=3`, `bombs=1`, `invuln_time=0s`.
- Actions: left/right movement clamped to playfield, `fire` spawns 1..N projectiles depending on power.
- Hit: lose life, set `invuln_time=1.5s`, reduce `power_level` by 1 (min 0).

### Enemy
- Types (v0.1): `grunt`, `dive`, `shooter`.
- Common: `hp`, `speed`, `pattern` (callable/state), `fire_interval` (for shooter), `drops` (prob table).
- Patterns:
  - Formation: row moves horizontally, steps down periodically.
  - Dive: enters at top, curves toward player x using simple sine or linear interpolation.
  - Shooter: like grunt but fires aimed bullets occasionally.

### Projectiles
- Fields: `owner` in {`player`, `enemy`}, `speed`, `damage=1`, `pierce=False` (v0.1 False).
- Movement: straight-line per tick; removed when off-screen.

### Systems
- Collision (AABB): spatial hash grid keyed by cell `(x//c, y//c)` with `c=2` or `c=3` chars; checks only neighboring cells.
- Spawner: time-based scheduler reading wave items; each item yields spawn events (enemy type, pos, params).
- Scoring: +10 per grunt, +15 shooter, +20 dive (v0.1), simple int in gameplay scene.

## Data-Driven Waves

### Minimal Wave Schema (v0.1)
- Top-level file: `data/waves.json` contains `{ "seed": int, "waves": [Wave] }`.
- `Wave` object fields (all optional except `type`):
  - `id`: string identifier.
  - `type`: `formation` | `dive` | `mixed` | `boss` (boss ignored in v0.1).
  - `duration`: seconds before auto-advance if enemies cleared (fallback by detection).
  - `spawn_rate`: spawns/second (for continuous patterns) or `null` for instant formation.
  - `count`: total enemies to spawn (if continuous).
  - `rows`: for formation (e.g., 1..3 rows).
  - `cols`: for formation (computed if omitted based on width).
  - `speed`: enemy baseline speed (cells/sec).
  - `fire_interval`: for shooter types; seconds between shots.
  - `patterns`: optional list when `type="mixed"`, each item mirrors the above at sub-scale with `weight`.
  - `drops`: probability table `{ "power": 0.2, "bomb": 0.05, "score": 0.3 }`.

Example (excerpt):
```json
{
  "seed": 1337,
  "waves": [
    {
      "id": "wave1",
      "type": "formation",
      "rows": 2,
      "cols": 8,
      "speed": 2.0,
      "drops": { "power": 0.2, "score": 0.3 }
    },
    {
      "id": "wave2",
      "type": "dive",
      "count": 18,
      "spawn_rate": 1.2,
      "speed": 3.0,
      "drops": { "power": 0.15, "score": 0.35 }
    },
    {
      "id": "wave3",
      "type": "mixed",
      "count": 24,
      "spawn_rate": 1.6,
      "patterns": [
        { "type": "grunt", "weight": 3 },
        { "type": "shooter", "weight": 1, "fire_interval": 2.0 }
      ],
      "speed": 2.3
    }
  ]
}
```

## Integration Plan (Phased)

1) Core entity scaffolding
- Add `core/entity.py` and migrate render hints from scene to entities.
- Minimal `World` container in `gameplay.py` to hold lists by `kind`.

2) Player entity and controls
- Implement `Player` with movement, fire cooldown, and invulnerability timer.
- Replace "^" drawing with `Player.sprite()`.

3) Projectiles and collision
- Implement `Projectile` entity; add broadphase + narrowphase AABB checks.
- Player projectiles damage enemies; enemy contact damages player.

4) Enemy types
- Implement `GruntEnemy`, `DiveEnemy`, `ShooterEnemy` with basic AI in `update()`.
- Shooter fires aimed bullets (simple linear aim toward player X).

5) Spawner system
- Inline wave config in `gameplay.py` first; then move to `data/waves.json`.
- Deterministic RNG from top-level `seed` per run; allow override.
- Advance wave when cleared or `duration` elapsed.

6) Scoring + HUD adjustments
- Award points on kill; show wave id and remaining enemies in HUD.
- Keep lives and bombs display.

7) Testing
- `tests/test_collision.py`: AABB and cell hashing edge cases.
- `tests/test_spawner.py`: Given seed and wave spec, verify spawn sequences (types/count/positions range).

## Risks & Mitigations
- Terminal flicker under load: cap to 30 FPS if draw time > TICK; keep entities modest.
- Input buffering misses: ensure nodelay and poll loop drain; maintain responsive fire cooldowns.
- Small terminals: clamp formation `cols` to width; spawn fewer enemies safely.

## Acceptance Criteria (for this feature set)
- Player, enemies, and projectiles are entities with update/collision logic.
- At least three enemy archetypes spawn via the spawner according to `waves.json`.
- Clearing a wave advances to the next; HUD shows score, lives, and wave id.
- Deterministic spawns when running with a fixed seed.
- Collision tests and spawner tests pass locally.
