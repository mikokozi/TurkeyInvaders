# Turkey Invaders (Terminal)

Turkey Invaders is a terminal-only arcade shooter inspired by Chicken Invaders, built with Python and curses. It runs entirely in your Ubuntu terminal and uses ASCII/Unicode characters for visuals.

## Quick Start
- Requirements: Python 3.10+
- Run: `python -m turkey_invaders`

## Controls (default)
- Move: Arrow keys or `WASD`
- Fire: `Space`
- Bomb: `X` or `x` (clears enemy bullets; limited). Only consumes a bomb if bullets are present to clear.
- Pause/Resume: `P`
- Options: `O` (from main menu)
- Quit: `Q` (menu or pause overlay)
- Help Overlay: `H` (menu, options, or in-game; pauses gameplay)
 - Exit Game: `Esc` (asks for confirmation)

## How To Play
- Goal: Clear waves of turkeys and avoid enemy fire.
- Start: Press `Enter` or `Space` on the main menu.
- Shoot: Press `Space` during gameplay to fire. Power-ups increase your shot spread.
- Move: Use arrow keys or `WASD` to dodge and line up shots.
- Bombs: Press `X` to clear enemy bullets (consumes 1 bomb). Pick up bomb power-ups to refill.
- Power-ups: Collect falling `P` (power) to boost firepower and `B` (bomb) to gain bombs.
- Pause: Press `P` to pause; press `Q` while paused to return to menu.
- Help: Press `H` anytime to open a quick controls/tips overlay.
 - Exit: Press `Esc` to bring up an exit confirmation. Use Left/Right to choose Yes/No and Enter to confirm.

## What’s Implemented
- Core loop with curses renderer and non-blocking input.
- Scenes: Menu, Gameplay, Game Over, Options, with pause overlay in-game.
- Entities: Player (lives, power level, bombs), Enemies (grunt, dive, shooter), Projectiles, Power-ups (power, bomb).
- Systems: Collision (AABB), Spawner (formation/dive/mixed) reading `data/waves.json` and seeded RNG.
- HUD: Score, Wave id, Lives, Power, Bombs.
- Config: Loads from `~/.config/turkey_invaders/config.json` (created on save from Options).

## Configuration
- File: `~/.config/turkey_invaders/config.json`
- Editable via the in-game Options screen (`O` in menu). Currently supports:
  - `fps` (30–120)
  - `scale` (1–4; increases on-screen size)
  - `drops.power` (0.0–1.0 probability)
  - `drops.bomb` (0.0–1.0 probability)
  - `controls` (action→keys; names like `LEFT`, `RIGHT`, `SPACE`, `ENTER` or single characters)

Example (partial):
```
{
  "fps": 60,
  "controls": { "fire": ["SPACE"], "bomb": ["x"] },
  "drops": { "power": 0.20, "bomb": 0.05 }
}
```

## Waves Data
- File: `turkey_invaders/data/waves.json`
- Defines the campaign and RNG seed. Current waves:
  - `wave1`: formation (rows/cols, slow sweep)
  - `wave2`: dive (timed spawns)
  - `wave3`: mixed (weighted grunt/shooter)
- See PRD section “Wave Definition Schema (v0.1)” for the schema overview.

## Project Structure (high level)
- `turkey_invaders/app.py`: bootstrap + fixed timestep loop
- `turkey_invaders/input.py`: key→action mapping (configurable)
- `turkey_invaders/render/`: curses renderer
- `turkey_invaders/scenes/`: menu, gameplay, options, gameover
- `turkey_invaders/core/`: entity base and world container
- `turkey_invaders/entities/`: player, enemies, projectiles, power-ups
- `turkey_invaders/systems/`: collision detection, spawner
- `turkey_invaders/data/`: `waves.json`
- `PRD.md`: product requirements and design

## Troubleshooting
- Terminal too small: Increase terminal size (80×24 minimum recommended).
- Colors not showing: Some terminals limit colors; basic attributes are used.
- Reset terminal after crash: run `reset` if the terminal looks garbled.
- Clear config: remove `~/.config/turkey_invaders/config.json` to restore defaults.

## Roadmap (next steps)
- Persistent high scores with initials prompt.
- Score multipliers and no-hit bonuses.
- Boss waves and additional enemy patterns.
- More options (key remap UI, color palettes), tests for collisions/spawner.
