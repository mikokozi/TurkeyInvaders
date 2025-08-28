# Turkey Invaders — Terminal Game PRD

## 1) Product Overview

Turkey Invaders is a fast-paced, terminal-only, arcade-style shooter inspired by the classic Chicken Invaders. The player controls a spaceship at the bottom of the screen, dodging falling eggs and shooting waves of turkeys that advance and attack in patterns. Gameplay is session-based, score-driven, and designed to be playable entirely inside a Unix terminal on Ubuntu using Python and curses.

## 2) Goals and Non‑Goals

### Goals
- Deliver a smooth, responsive shooter that runs in a terminal (80×24 minimum) on Ubuntu.
- Emulate the core feel of Chicken Invaders: waves, drops, upgrades, bosses, humor.
- Provide deterministic, testable game logic decoupled from rendering.
- Support persistent high scores and basic configuration.
- Ship with no non‑stdlib hard dependencies (use Python `curses`); allow optional niceties.

### Non‑Goals (Initial Releases)
- No mouse, gamepad, or network multiplayer (single keyboard only).
- No external assets (images/audio) required to play; purely text/ASCII/Unicode.
- No Windows support (curses on Windows is non‑trivial; may come later).
- No save‑and‑resume mid‑run; sessions are short and score-based.

## 3) User Stories
- As a player, I want to start the game from the terminal and immediately play with intuitive controls.
- As a player, I want progression through themed waves culminating in boss fights.
- As a player, I want visible power‑ups to change my weapon and feel stronger.
- As a player, I want clear feedback when hit, and a fair but escalating challenge.
- As a player, I want to compare my score across runs (local high scores).
- As a player, I want the game to accommodate different terminal sizes where possible.

## 4) Gameplay

### Core Loop
- Navigate the ship along the bottom row(s) to dodge falling projectiles.
- Shoot upwards to clear enemies; collect drops for upgrades or score.
- Survive waves; defeat bosses; chase high scores; repeat until lives reach zero.

### Controls (Default)
- Left/Right: Arrow keys or `A` `D`
- Up/Down (rarely needed): Arrow keys or `W` `S` (for special patterns)
- Fire: `Space`
- Focus/Precision (slower movement): `Left Shift`
- Bomb/Clear Screen (limited): `X`
- Pause/Resume: `P`
- Quit to menu: `Q`

Configurable via config file; detect key conflicts and show help overlay (`H`).

### Player Mechanics
- Lives: 3 (configurable). On hit, lose a life and short invulnerability (1.5s).
- Movement: Horizontal constrained to playfield; vertical limited to bottom third.
- Firing:
  - Base weapon: Single shot, 6/s, small damage.
  - Heat/Overheat (optional): Continuous firing increases heat; on overheat, cooldown.
  - Power levels: 0–10; drops increment power; death reduces by 2.
  - Alternate weapons: Spread, laser (piercing with recharge), rockets (slow, splash).
- Bombs: Start 1; clears bullets, stuns small enemies briefly; drops can add more.

### Enemies
- Types: 
  - Grunt Turkey: slow, in formations; drops eggs.
  - Divebomber: charges player in arcs.
  - Shooter: fires aimed shots at intervals.
  - Armored: takes multiple hits; slower.
  - Egg Cluster: destructible hazard; breaks into fragments.
- Behaviors: pattern movement (sine, zigzag, column sweep), periodic attacks, telegraphs.

### Bosses
- Every N waves (e.g., 5). Multi‑phase with health bar.
- Attacks: bullet curtains (simple), aimed bursts, sweeping lasers (telegraphed with charge).
- Breakpoints: behavior changes at 75/50/25% health; minion spawns.

### Waves and Progression
- Session length target: 10–20 minutes to clear all stages or die.
- Wave templates combined with parameters:
  - Rows of turkeys moving left-right, gradually descending.
  - Rotating rings; diagonal sweeps; staggered spawn lanes; dive waves.
  - Intermissions: meteor/food showers for bonus points.
- Difficulty scaling: spawn rate, projectile speed, enemy HP and aggression over time.

### Scoring & Rewards
- Points for enemy kills; multipliers for streaks and no‑hit waves.
- Drops: 
  - Power‑up (+1 power level).
  - Drumstick (score bonus).
  - Bomb.
  - Shield (short invulnerability).
  - Coin (currency for shop runs — later feature).
- High scores saved locally with initials prompt at end.

### Hitboxes & Collisions
- Grid cell resolution equals character cells. Entities have bounding boxes in cell units.
- Bullets treated as points or 1×1 boxes; fast projectiles use swept collision.
- Friendly fire off; enemies collide with player; enemies do not collide with each other.

### Visual Style (Terminal)
- Characters: ASCII/Unicode sprites for player, enemies, bullets, power‑ups.
- Colors: 16 basic colors; bold for emphasis. Optional truecolor if supported.
- Screen: fixed HUD area at top; playfield below; double‑buffered redraw each tick.
- Effects: minimal particle trails using lightweight character noise; flash on damage.

### Audio (Optional)
- Terminal bell for hits/drops via `curses.beep()`; optional `simpleaudio`/`pygame.mixer` if user installs, but not required.

## 5) Technical Design

### Architecture
- Layered design separating Update (game state), Render (terminal), Input, and Scene management.
- Deterministic update loop at fixed timestep (e.g., 60 Hz or 30 Hz) with interpolation disabled (terminal redraw each tick).
- All timing based on monotonic clocks; frame skipping allowed to catch up.

### Module Layout
```
./turkey_invaders/
  __init__.py
  __main__.py        # CLI entry: python -m turkey_invaders
  app.py             # Game bootstrap, main loop
  config.py          # Load/save defaults, keybinds, palette
  input.py           # Non-blocking key handling, mapping
  render/
    __init__.py
    curses_renderer.py  # All ncurses drawing
    dummy_renderer.py   # Headless renderer for tests
  scenes/
    __init__.py
    base.py
    menu.py
    gameplay.py
    gameover.py
  core/
    __init__.py
    ecs.py           # Optional light ECS or entity base classes
    entity.py        # Base entity with position, bbox, update()
    physics.py       # Movement, collision detection, spatial hashing grid
    rng.py           # Seeded RNG for deterministic tests
    timer.py         # Reusable timers/cooldowns
  entities/
    player.py
    enemy.py
    boss.py
    projectile.py
    powerup.py
    particle.py
  systems/
    collision.py
    spawner.py       # Wave scripting and spawning
    scoring.py
    hud.py
  data/
    waves.json       # Wave patterns & params (human-editable)
    sprites.tiart    # ASCII/Unicode sprite definitions (optional)
  assets/            # Empty by default; future optional sounds

./tests/
  test_collision.py
  test_spawner.py
  test_input.py

README.md
PRD.md
```

### Key Data Structures
- Vector2: integer grid coordinates `(x, y)`.
- Rect: `(x, y, w, h)` for bounding boxes.
- Entity: `id`, `pos`, `vel`, `bbox`, `flags`, `update(dt)`, `render(rndr)`.
- World: lists or dicts of entities by type; spatial grid map: `cell -> [entity ids]`.
- Event Bus: lightweight pub/sub for pickups, damage, deaths.

### Game Loop (Pseudocode)
```
init_curses()
world = World()
scene = Menu()
accumulator = 0
last = now()
TICK = 1/60  # fallback to 1/30 if slow terminal

while running:
  now_t = now()
  accumulator += now_t - last
  last = now_t

  # Input
  for key in input.poll():
    scene.handle_input(key)

  # Fixed updates
  while accumulator >= TICK:
    scene.update(TICK)
    accumulator -= TICK

  # Render
  renderer.begin_frame()
  scene.render(renderer)
  renderer.end_frame()
```

### Rendering (curses)
- Use `curses.wrapper()` to initialize and restore terminal state.
- Enable `nodelay(True)` and `keypad(True)`; poll using `getch()` without blocking.
- Maintain an off‑screen buffer (2D array of cells with char+color) and draw diff each frame to reduce flicker.
- Handle terminal resize via `SIGWINCH`; adapt HUD and playfield; pause if too small.

### Input
- Key mapping table from `curses` codes to actions; allow overriding in config.
- Debounce and repeat handling for held keys.
- Input layer produces a set of actions per frame (move_left, fire, pause, bomb).

### Physics & Collision
- Movement: per‑tick position updates; clamp to boundaries.
- Collision: discrete grid AABB checks; spatial hash by cells to keep checks O(n).
- Swept collision for fast bullets: check along path between previous and new position.

### Spawning & Waves
- Wave definitions in `data/waves.json`, supporting:
  - `type`: formation, dive, ring, boss, etc.
  - `count`, `hp`, `speed`, `fire_rate`, `pattern_params`.
  - `drops`: probability table for item types.
- Spawner interprets and schedules spawns; emits events for HUD and audio cues.

### Persistence
- High scores in `~/.local/share/turkey_invaders/highscores.json`.
- Config in `~/.config/turkey_invaders/config.json`.
- Files created lazily; handle permissions errors gracefully; never crash on write.

### Configuration
- Screen: target FPS (30/60), color palette, show_fps (bool).
- Gameplay: lives, bomb_start, difficulty multiplier.
- Controls: key mapping by action.
- Accessibility: colorblind palette, reduced flash mode, slow mode.

## 6) Content Specification

### Sprites (ASCII/Unicode)
- Player: `^` or `⮝` with wings using `/<` and `\>` style embellishments.
- Turkeys: `U` with tail `{}` or compact `@` variants; bosses larger multi‑cell.
- Bullets: `|` for lasers, `•` for pellets, `^`/`v` for arrows.
- Power‑ups: `*` star, `B` bomb, `S` shield, `P` power core.
- HUD: hearts `♥` or `❤` for lives; small icons for bombs.

### Waves (Initial Set)
- 1: Gentle formation left-right, slow eggs.
- 2: Two rows, staggered speeds; first drops appear.
- 3: Divebombers in arcs.
- 4: Rotating ring that contracts; projectiles slow.
- 5: Boss 1: Big Turkey — egg bursts and charges.
- 6–9: Increased aggression; add armored and shooters; intermission shower.
- 10: Boss 2: Mecha Turkey — sweeping lasers and minion spawns.

### Pickups & Probabilities (Baseline)
- Power‑up: 20%
- Drumstick (score): 30%
- Bomb: 5%
- Shield: 10%
- Nothing: 35%

## 7) UX & UI
- Main Menu: Start, Options, High Scores, Quit.
- Options: keybinds, colors, difficulty, FPS.
- In‑Game HUD: score (left), lives/bombs (center), weapon level/heat (right), wave/phase (top‑right).
- Pause Screen: resume, restart, quit; show controls.
- Game Over: score summary, enter initials for leaderboard.

## 8) Performance Targets
- 60 FPS target; 30 FPS minimum under load.
- CPU budget: < 10% on typical laptop core at 60 FPS for baseline waves.
- Memory: < 100 MB RSS.
- Draw budget: diff‑based rendering < 10% of cells per frame changed on average.

## 9) Testing Strategy
- Unit tests:
  - Collision detection (AABB, swept).
  - Spawner schedules (given seed, spawns match spec).
  - Input mapping (keys translate to actions).
  - Timer/cooldown behavior.
- Integration tests:
  - Headless `dummy_renderer` + deterministic RNG to simulate waves and verify state.
- Manual tests:
  - Resize behavior; minimal terminal sizes; key repeat; pause/resume; FPS under stress.

## 10) Risks & Mitigations
- Terminal refresh flicker: use off‑screen buffer and diff draws; cap FPS.
- Key rollover limits: provide alternative bindings; accept simultaneous arrow + space.
- Small terminals: pause and prompt to enlarge; scale formations.
- Performance on remote terminals: auto‑drop to 30 FPS; reduce particle effects.
- Curses variability across terminals: avoid exotic attributes; detect capabilities.

## 11) Roadmap

### MVP (v0.1)
- Curses renderer, input system, fixed timestep loop.
- Player movement, shooting, basic power‑ups.
- 4–6 wave templates, 1 boss.
- HUD, pause, game over, high scores.
- Basic tests (collision, spawner, input).

### v0.2
- Additional enemies and patterns; second boss.
- Heat/overheat system; more weapons.
- Options UI; accessibility options; color palettes.
- Performance tuning; more tests; refactor to ECS if needed.

### v1.0
- Full 10‑wave campaign with 2 bosses + intermissions.
- Local co‑op (two players on one keyboard) if feasible.
- Achievements; polish; optional audio support.

## 12) Implementation Notes (Ubuntu/Python)
- Python 3.10+ recommended.
- Use built‑in `curses` (`apt install python3` already includes it on Ubuntu). For development: `sudo apt install python3-dev` if compiling optional modules.
- Ensure terminal supports UTF‑8; fallback to pure ASCII if not.
- Run via `python -m turkey_invaders` once package is scaffolded.

## 13) Acceptance Criteria (MVP)
- Game launches in terminal and returns terminal to normal state on exit.
- Player can move and shoot; enemies spawn, move, and can be destroyed.
- At least 4 distinct waves and 1 boss are playable.
- Power‑ups affect weapon; bombs clear bullets; lives and scoring work.
- High scores persist between sessions; options can be changed via config file.
- Stable at 30 FPS on 80×24 in a default Ubuntu terminal.

---
This PRD aims to be specific enough to implement in iterative slices, with rendering abstracted for testability and content defined in data files for rapid tuning.

## 14) Wave Definition Schema (v0.1)

- File: `data/waves.json`
- Structure:
  - `seed` (int): RNG seed for deterministic spawns.
  - `waves` (array): list of wave objects.
- Wave fields:
  - `id` (string): identifier.
  - `type` (string): `formation` | `dive` | `mixed` | `boss`.
  - `duration` (float, optional): seconds to auto-advance if not cleared.
  - `spawn_rate` (float, optional): spawns per second for continuous waves.
  - `count` (int, optional): total enemies when using continuous spawns.
  - `rows` (int, optional): formation rows.
  - `cols` (int, optional): formation columns.
  - `speed` (float, optional): baseline speed.
  - `fire_interval` (float, optional): for `shooter` enemies.
  - `patterns` (array, optional): for `mixed` waves; each with `type`, `weight`, and overrides.
  - `drops` (object, optional): probability table (e.g., `{ "power": 0.2, "bomb": 0.05, "score": 0.3 }`).

Example:
```
{
  "seed": 1337,
  "waves": [
    { "id": "wave1", "type": "formation", "rows": 2, "cols": 8, "speed": 2.0 },
    { "id": "wave2", "type": "dive", "count": 18, "spawn_rate": 1.2, "speed": 3.0 }
  ]
}
```

## 15) Entity Model (v0.1)

- Base entity: `id`, `kind`, `x`, `y`, `w`, `h`, `vx`, `vy`, `hp`, `alive`.
- Player: `speed`, `fire_cooldown`, `power_level`, `lives`, `bombs`, `invuln_time`.
- Enemies: `type`, `hp`, `speed`, `pattern`, `fire_interval`, `drops`.
- Projectile: `owner`, `speed`, `damage`, `pierce` (false in v0.1).
- Collision: grid-based AABB; swept optional for fast projectiles later.

## 16) Current Implementation Status (v0.1 WIP)

- Loop/Renderer/Input:
  - Curses renderer with diff-friendly drawing and color pairs.
  - Non-blocking input with configurable action→keys mapping.
  - Fixed-timestep loop with configurable FPS (30–120).
- Scenes:
  - Menu, Gameplay, Game Over, Options; in-game pause overlay.
- Entities/Systems:
  - Player with lives, bombs, power level, fire cooldown, invulnerability.
  - Enemies: grunt (formation sweep), dive (sine wobble toward player), shooter (patrol + downward fire).
  - Projectiles (player/enemy) with frame-rate independent movement.
  - Power-ups: power and bomb drops with configurable probabilities.
  - Collision system: AABB for player/enemy, bullets vs enemies, enemy bullets vs player, player vs pickups.
  - Spawner: reads `turkey_invaders/data/waves.json`, supports `formation`, `dive`, and `mixed` types; deterministic via seed.
- HUD:
  - Score, current wave id, lives, power level, bombs. Pause overlay.
- Config:
  - Loads/merges from `~/.config/turkey_invaders/config.json`. Options scene saves user changes.

Pending (next milestones):
- High scores (persistent) and end-run initials prompt.
- Score multipliers and no-hit bonuses per wave.
- Boss waves, additional patterns, tuning, and tests for collision/spawner.
