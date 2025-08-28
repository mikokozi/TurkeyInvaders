# Turkey Invaders (Terminal) — Codebase Audit Report

Date: 2025-08-28
Scope: Functional review, error/bug risks, and maintainability of the Python terminal game in `turkey_invaders/`.

## Executive Summary

- The codebase is a clean, minimal, runnable terminal shooter prototype with scenes, rendering, input, entities, and basic systems (spawner, collision). A headless mode enables CI-friendly smoke tests.
- Core loop, scene transitions, entity updates, and rendering work as advertised. A quick headless run shows frames rendering without errors.
- Notable issues: frame-step handling is not a true fixed timestep (simulation slows under load), player movement depends on OS key-repeat and frame rate, spawner’s one-shot formation spawn uses a brittle float-equality check, and error handling for config load/save could mask problems. Repo hygiene items (`__pycache__`, `.venv`, `.idea`) are tracked in-tree.
- No fatal blockers detected; recommended fixes are medium-to-low effort and will improve determinism, UX, and robustness.

## How To Run (Validated)

- Headless smoke: `TI_HEADLESS=1 TI_HEADLESS_SECONDS=0.2 python3 -m turkey_invaders`
- Normal (curses): `python3 -m turkey_invaders` (in a real terminal)
- Helper script: `./start.sh [--headless [seconds]]`

## Architecture Overview

- Entry: `turkey_invaders/__main__.py` → `app.main()`
- Loop: `turkey_invaders/app.py` provides curses and headless modes; per-frame input → update → render.
- Rendering: `render/curses_renderer.py` and `render/stdout_renderer.py` with a minimal API `draw_text`, `begin_frame`, `end_frame`.
- Scenes: `scenes/menu.py`, `scenes/gameplay.py`, `scenes/options.py`, `scenes/gameover.py` (base in `scenes/base.py`).
- Core: `core/entity.py` (base entity), `core/world.py` (container, ids, kind index).
- Entities: `entities/player.py`, `entities/enemy.py` (grunt, dive, shooter), `entities/projectile.py`, `entities/powerup.py`.
- Systems: `systems/collision.py` (AABB), `systems/spawner.py` (waves from `data/waves.json`).
- Config: `config.py` loads/merges defaults with `~/.config/turkey_invaders/config.json`.

## Key Findings

### Medium Severity

- Fixed timestep not respected under load
  - Files: `turkey_invaders/app.py`
  - Issue: The main loop uses a single update per frame: `if accumulator >= tick: update(); accumulator = 0.0`. When frames take longer than `tick`, extra accumulated time is discarded, slowing simulation rather than catching up. The PRD suggests a fixed timestep with frame skipping allowed.
  - Impact: Game runs slower than real time on slow frames; spawns, cooldowns, and timers slip.
  - Recommendation: Use a while-loop: `while accumulator >= tick: scene.update(tick); accumulator -= tick` and cap max substeps per frame (e.g., 4) to avoid spiral-of-death.
  - Status: Implemented (capped catch-up in both curses and headless loops).

- Player movement tied to key repeat / frame rate
  - Files: `turkey_invaders/scenes/gameplay.py`, `entities/player.py`
  - Issue: Movement increments position by 1 cell per frame/input event, ignoring `Player.speed` and `dt`. Behavior depends on terminal key repeat and frame rate.
  - Impact: Inconsistent movement speed; poor feel across environments.
  - Recommendation: Track held directions (left/right/up/down) as persistent state and move using `speed * dt` with subcell accumulation, similar to projectiles.
  - Status: Implemented (dt-based movement plus short hold timers for smoothing).

- Brittle float equality for formation spawn
  - Files: `turkey_invaders/systems/spawner.py`
  - Code: `if wave.get("type") == "formation": if self.timer == dt: self._spawn_formation(wave)`
  - Issue: Compares floats for exact equality; fragile if dt varies or timer isn’t exactly `dt`.
  - Impact: Potential missed formation spawns in edge cases.
  - Recommendation: Replace with an explicit boolean `spawned_once` flag per wave, or check `if self.timer <= dt + 1e-9 and not spawned:`.
  - Status: Implemented (one-shot flag per wave; reset on advance).

- Config error handling may hide problems
  - Files: `turkey_invaders/config.py`
  - Issue: `load_config()` swallows all exceptions (`except Exception: pass`), losing visibility into malformed JSON or permission issues. `save()` does not handle IO errors.
  - Impact: Silent fallback to defaults; confusing for users who edited config.
  - Recommendation: Catch specific exceptions, log/print a concise warning in headless and curses modes (e.g., “Invalid config JSON at …; using defaults”), and handle `save()` failures gracefully.
  - Status: Implemented (warnings collected on load/save; printed in headless mode).

### Low Severity

- Scene render duplication
  - Files: `turkey_invaders/scenes/gameplay.py`
  - Issue: `Score:` is drawn twice in the same frame (once early, once in “HUD extras”).
  - Impact: Redundant calls; minor overhead/clutter.
  - Recommendation: Remove the duplicate draw.

- Game Over prompt mismatch
  - Files: `turkey_invaders/scenes/gameover.py`
  - Issue: UI says “Press Q to exit” but `start` and `fire` also exit.
  - Impact: UX inconsistency.
  - Recommendation: Update prompt to reflect all accepted keys or restrict to `Q`.

- Enemy update assumes `world.player` exists
  - Files: `turkey_invaders/entities/enemy.py`
  - Issue: Calls `world.player.on_player_hit()` without explicitly checking for `None`.
  - Context: Current scene order ensures player exists before spawns; still brittle if reused elsewhere/tests.
  - Recommendation: Guard for `world.player is not None` or make world provide a safe no-op handler.

- Weighted choice edge handling
  - Files: `turkey_invaders/systems/spawner.py`
  - Note: Uses `random.uniform(0, total)` and `>=` threshold checks, with fallback to last item. Behavior is acceptable, but using `random.random()*total` and `>`/`>=` consistently can be clearer.

- Repo hygiene
  - Files/Dirs: `turkey_invaders/__pycache__/`, `.venv/`, `.idea/`
  - Issue: Build artifacts and editor/venv folders are tracked.
  - Recommendation: Add a `.gitignore` to exclude `__pycache__/`, `*.pyc`, `.venv/`, `.idea/`.

### Informational / Enhancements

- Tests missing
  - PRD calls for unit tests (collision, spawner, input). None are present.
  - Suggest: Add a `tests/` dir with fast headless tests, including deterministic spawner tests using `seed`.

- Input conflicts
  - Files: `turkey_invaders/input.py`
  - Observation: Multiple actions can bind to the same key with last-wins; no conflict diagnostics.
  - Suggest: Warn on conflicts during binding compilation; consider per-frame “held” state for movement.

- Shooter projectile speed tuning
  - Files: `entities/enemy.py`
  - Observation: Shooter bullets move at ~1 cell/sec; may feel trivial.
  - Suggest: Increase speed based on wave difficulty or config.

- Packaging metadata
  - No `pyproject.toml`/`setup.cfg` for distribution. If you plan to package or publish, add standard metadata.

## Code Quality Notes

- Rendering and input abstractions are small and easy to reason about.
- Entities use time-accumulator stepping for smooth, frame-rate independent motion; good approach worth extending to player movement.
- Error handling generally errs on the side of “don’t crash”, but a few places swallow exceptions silently; prefer visible, concise warnings.

## Quick Fixes (Suggested Patch Plan)

1) Fix timestep handling in `app.py`:
   - Replace single-step update with a loop: `while accumulator >= tick: update(tick); accumulator -= tick` and cap substeps.

2) Make formation spawning robust:
   - Track `self._formation_spawned` per wave index or check `self.timer <= dt + eps`.

3) Make player movement dt-based:
   - Track held directions in `GameplayScene` and apply `Player.speed * dt` with an accumulator to move whole cells.
   - Status: Implemented.

4) Improve config error handling and messaging:
   - Log a short warning on invalid JSON/IO errors; avoid silent `pass`.
   - Status: Implemented; see also headless warning printouts.

5) Minor HUD/UI cleanups:
   - Remove duplicate `Score:` draw; update Game Over prompt.

6) Add `.gitignore`:
   - Exclude `__pycache__/`, `*.pyc`, `.venv/`, `.idea/`.

## Verification Checklist (Post-Fix)

- Under simulated low FPS, game time (spawns, cooldowns) remains consistent with a real-time stopwatch.
- Holding movement keys moves at the same perceived speed regardless of terminal frame rate/key repeat.
- Formation waves always spawn once at wave start.
- Config edits with invalid JSON produce a visible warning but do not crash; valid edits are applied.
- UI prompts match accepted keys; HUD shows each field once.
- Headless run prints consistent frames; basic unit tests pass.

## Appendix: File Inventory

- Entrypoints: `turkey_invaders/__main__.py`, `start.sh`
- Loop/Config: `turkey_invaders/app.py`, `turkey_invaders/config.py`
- IO/Render: `turkey_invaders/input.py`, `turkey_invaders/render/*`
- Scenes: `turkey_invaders/scenes/*`
- Entities/Core: `turkey_invaders/core/*`, `turkey_invaders/entities/*`
- Systems: `turkey_invaders/systems/*`
- Data: `turkey_invaders/data/waves.json`
