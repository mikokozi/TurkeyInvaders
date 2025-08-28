# Changelog

## v0.1.0 — 2025-08-28 (Final for Today)

Stabilization and audit fixes for the terminal game MVP:

- Fixed timestep loop with capped catch-up (curses + headless).
- dt-based player movement with sub-cell accumulators and short hold smoothing.
- Robust formation spawning (one-shot flag) instead of fragile float checks.
- Config: collect warnings on load/save issues; headless prints [config] messages.
- HUD/UI: remove duplicate Score draw; clarify Game Over prompt.
- Renderer scaling supported (curses + headless); headless respects TI_SCALE.
- Repo hygiene: add .gitignore for venv/pycache/IDE files.
- Tests: add minimal unit tests for collisions, spawner, and input mappings.

---

## 2025-08-28

Scope: make the terminal shooter playable end-to-end with better UX, visuals, audio, and CLI ergonomics.

- Startup fixes
  - Break circular import between `MenuScene` and `GameplayScene` by lazy-importing the menu inside gameplay.
  - Initialize `World.player`, `World.width`, `World.height` to avoid attribute errors on early ticks.

- Run workflow
  - Add `start.sh` to create/activate `.venv`, (optionally) install `requirements.txt`, and run the game.
  - Add headless mode: `TI_HEADLESS=1` renders frames to stdout for quick CI/smoke checks.
  - Add `stdout_renderer` and config/env controls: `TI_HEADLESS_SECONDS`, `TI_TERM_WIDTH/HEIGHT`, `TI_SCALE`.

- Input & UX
  - Help overlays: Menu, Options, and in-game help (press `H`) with concise controls and tips.
  - Exit confirmation: press `Esc` anywhere to open Yes/No dialog; Left/Right to toggle, Enter or Y/N to confirm.
  - Input mapping improvements:
    - Preserve earlier bindings so `fire=SPACE` isn’t overridden by `start=SPACE`.
    - Single-letter actions are case-insensitive (e.g., `x` and `X` for bombs).

- Gameplay
  - Bombs: clear enemy bullets; only consume a bomb if anything is actually cleared; "BOMB!" flash indicator.
  - Movement smoothing: hold-based movement intent with sub-cell accumulators for consistent dt-based motion.
  - Chicken ASCII sprites for player and enemies (always on).
  - Expanded colors: player, enemies, player/enemy projectiles, power-ups, HUD.
  - Audio SFX: fire, bomb, hit, powerup, confirm, gameover (with optional `simpleaudio` and terminal-bell fallback).
  - Background music: simple looping tunes in Menu and Gameplay (toggle in Options).
  - Arcade polish: score popups on kills, combo scoring window (~1.5s), and subtle screen shake on player hit.

- Options & Config
  - New `Scale` option (1–4x) to enlarge all visuals; applies live during gameplay.
  - New `audio.music` and `audio.sfx` flags; toggles available in Options.
  - Existing: `fps`, `drops.power`, `drops.bomb`, `controls` mapping.

- Docs
  - README expanded with How to Play, Help overlay, Scale, Audio (optional), and troubleshooting.
  - Added headless usage notes and start.sh examples.
