import os
import time
import curses

from .render.curses_renderer import CursesRenderer
from .render.stdout_renderer import StdoutRenderer
from .input import Input
from .scenes.menu import MenuScene
from .config import load_config
from .audio import set_sfx_enabled, set_music_enabled


def main() -> None:
    """Launch the game.

    Normal mode uses curses. If environment variable TI_HEADLESS is set to a
    truthy value, run in a headless text mode suitable for CI/smoke tests.
    Optional envs:
      - TI_HEADLESS_SECONDS: duration to run (default: 0.2)
      - TI_TERM_WIDTH / TI_TERM_HEIGHT: viewport size (default: 80x24)
    """
    if _env_truthy("TI_HEADLESS"):
        seconds = float(os.environ.get("TI_HEADLESS_SECONDS", "0.2"))
        width = int(os.environ.get("TI_TERM_WIDTH", "80"))
        height = int(os.environ.get("TI_TERM_HEIGHT", "24"))
        _run_headless(seconds=seconds, width=width, height=height)
    else:
        curses.wrapper(_run)


def _env_truthy(name: str) -> bool:
    val = os.environ.get(name, "")
    return val.lower() in {"1", "true", "yes", "on"}


def _run(stdscr) -> None:
    # Basic terminal setup
    stdscr.nodelay(True)
    stdscr.keypad(True)
    try:
        curses.curs_set(0)
    except Exception:
        pass

    cfg = load_config()
    set_sfx_enabled(bool(cfg.audio.get('sfx', True)))
    set_music_enabled(bool(cfg.audio.get('music', True)))
    renderer = CursesRenderer(stdscr, scale=cfg.scale)
    input_sys = Input(stdscr, controls=cfg.controls)

    current_scene = MenuScene(config=cfg)
    running = True
    # Global exit confirmation state
    confirm_exit = False
    confirm_choice = 1  # 0 = Yes, 1 = No (default safe)

    fps = max(15, min(120, cfg.fps))
    tick = 1.0 / float(fps)
    last = time.monotonic()
    accumulator = 0.0

    # Allow a limited number of catch-up steps to avoid spiral-of-death
    max_substeps = 4
    while running:
        now = time.monotonic()
        frame_time = now - last
        last = now
        accumulator += frame_time

        # Input
        actions = input_sys.poll()
        # ESC -> open exit confirmation overlay
        if 'exit' in actions:
            confirm_exit = True
            confirm_choice = 1
        if not confirm_exit:
            current_scene.handle_actions(actions)

        # Fixed update with catch-up and cap
        steps = 0
        while accumulator >= tick and steps < max_substeps:
            if not confirm_exit:
                current_scene.update(tick)
            accumulator -= tick
            steps += 1
        if steps == max_substeps and accumulator >= tick:
            # Drop leftover to keep real-time pace
            accumulator = 0.0

        # Render
        renderer.begin_frame()
        current_scene.render(renderer)
        if confirm_exit:
            _render_confirm_exit(renderer, confirm_choice)
        renderer.end_frame()

        # Apply runtime scale changes from options (no restart needed)
        try:
            renderer.scale = cfg.scale  # type: ignore[attr-defined]
        except Exception:
            pass

        if confirm_exit:
            # Handle confirm input
            if 'left' in actions or 'right' in actions:
                confirm_choice = 1 - confirm_choice
            if 'yes' in actions:
                confirm_choice = 0
            if 'no' in actions:
                confirm_choice = 1
            if 'start' in actions:
                if confirm_choice == 0:
                    running = False
                else:
                    confirm_exit = False
            # Also allow pressing 'quit' or 'pause' to cancel
            if 'quit' in actions or 'pause' in actions:
                confirm_exit = False
        else:
            if getattr(current_scene, "exit_program", False):
                running = False
            elif getattr(current_scene, "next_scene", None) is not None:
                current_scene = current_scene.next_scene

        # Frame cap
        elapsed = time.monotonic() - now
        sleep_for = tick - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)


def _run_headless(*, seconds: float, width: int, height: int) -> None:
    """Minimal non-curses run that renders to stdout.

    Runs the main loop for a limited time without input.
    """
    cfg = load_config()
    # Print config warnings in headless mode
    if getattr(cfg, 'warnings', None):
        for wmsg in cfg.warnings:
            print(f"[config] {wmsg}")
    # Allow overriding scale via TI_SCALE in headless, else use config
    try:
        scale = int(os.environ.get("TI_SCALE", str(load_config().scale)))
    except Exception:
        scale = load_config().scale
    renderer = StdoutRenderer(width=width, height=height, scale=scale)

    current_scene = MenuScene(config=cfg)
    running = True
    confirm_exit = False
    confirm_choice = 1

    fps = max(1, min(10, int(cfg.fps)))  # keep output small
    tick = 1.0 / float(fps)
    last = time.monotonic()
    end_time = last + max(0.05, seconds)
    accumulator = 0.0

    # Allow a limited number of catch-up steps to avoid spiral-of-death
    max_substeps = 3
    while running and time.monotonic() < end_time:
        now = time.monotonic()
        frame_time = now - last
        last = now
        accumulator += frame_time

        # No input in headless mode
        actions = set()
        if not confirm_exit:
            current_scene.handle_actions(actions)

        # Fixed update with catch-up and cap
        steps = 0
        while accumulator >= tick and steps < max_substeps:
            current_scene.update(tick)
            accumulator -= tick
            steps += 1
        if steps == max_substeps and accumulator >= tick:
            accumulator = 0.0

        # Render
        renderer.begin_frame()
        current_scene.render(renderer)
        if confirm_exit:
            _render_confirm_exit(renderer, confirm_choice)
        renderer.end_frame()

        if confirm_exit:
            # Auto-cancel in headless mode
            confirm_exit = False
        else:
            if getattr(current_scene, "exit_program", False):
                running = False
            elif getattr(current_scene, "next_scene", None) is not None:
                current_scene = current_scene.next_scene

        # Frame cap
        elapsed = time.monotonic() - now
        sleep_for = tick - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)


def _render_confirm_exit(r, choice: int) -> None:
    w, h = r.get_size()
    options = ["Yes", "No"]
    sel_yes = choice == 0
    yes_lbl = f"[{options[0]}]" if sel_yes else "  Yes  "
    no_lbl = f"[{options[1]}]" if not sel_yes else "  No   "
    lines = [
        "Exit game?",
        "",
        f"{yes_lbl}   {no_lbl}",
        "Enter: select   Left/Right: toggle   Q: cancel",
    ]
    box_w = max(len(s) for s in lines) + 4
    box_h = len(lines) + 2
    x0 = max(0, w // 2 - box_w // 2)
    y0 = max(0, h // 2 - box_h // 2)
    r.draw_text(x0, y0, "+" + "-" * (box_w - 2) + "+", color_pair=1)
    for i, s in enumerate(lines, start=1):
        r.draw_text(x0, y0 + i, "| " + s.ljust(box_w - 4) + " |", color_pair=1)
    r.draw_text(x0, y0 + box_h - 1, "+" + "-" * (box_w - 2) + "+", color_pair=1)
