# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A starter repository FIRST LEGO League teams fork to write Pybricks programs for LEGO SPIKE Prime robots. The audience is kids and coaches who are beginner programmers — keep code simple, flat, and heavily commented. Code does **not** run on the host machine — it is uploaded to the hub over BLE and runs there on Pybricks's MicroPython port. Most of the standard library is unavailable on the hub.

## Running code on the robot

Code is uploaded and run via `pybricksdev` (wrapped by `.vscode/run_pybricks.py`, which terminates the debug session cleanly when the program on the hub exits). Use the VS Code debug configurations:

- **Pybricks: Run on Robot** — runs the currently open file on the robot named in `.vscode/settings.json` (`pybricks.robotName`).
- **Pybricks: Run on Robot (Select)** — prompts to pick from a list in `.vscode/launch.json` (teams edit this to match their hubs).

From the CLI, the equivalent is `python -m pybricksdev run --name <RobotName> ble <file.py>`. The hub must be on and in range; `pybricksdev` connects via BLE. `pybricksdev run` bundles sibling-module imports (e.g. `robot`, `menu`, `pix_display`) into the upload, which is why the flat single-directory layout matters.

There are no tests, build step, or lint config wired up. `black` is in `requirements.txt` for manual formatting.

## Architecture

### `robot.py` — single source of truth for hardware config
The only file teams edit when their robot's build changes. An "EDIT THIS SECTION" banner at the top holds constants: wheel ports/directions, `WHEEL_DIAMETER_MM`, `AXLE_TRACK_MM`, attachment motor ports, sensor ports, `USE_GYRO`. Optional hardware uses `None` (some teams have one attachment motor and no sensors). The `Robot` class constructs `hub`, wheel motors, a `DriveBase` (with `use_gyro`), and sets each optional attribute (`attachment_1`, `attachment_2`, `color_sensor`, `distance_sensor`, `force_sensor`) to a device or `None`. Also exports `inches(n)` — Pybricks uses mm, FLL mats are measured in inches. Hardware is deliberately constructed in `Robot.__init__`, not at import time, so a missing motor fails at a clear call site.

### Mission files — `mission_NN_<name>.py`
Every mission has the same shape: a module docstring, `def run(robot):` with the moves, and an `if __name__ == "__main__": run(Robot())` block so it is standalone-runnable (open the file, press F5). The `NN` in the filename matches the number registered in `main.py`'s menu — the number shown on the hub's display. `mission_template.py` is the copy-me skeleton and is intentionally not registered in the menu.

### `main.py` — competition entry point
Builds a `Robot`, builds a `Menu(robot.hub, context=robot)`, registers each mission's `run` with its display number, and calls `menu.run(auto_increment=True)` (advance to the next mission after each run — match-friendly).

### `menu.py` — `Menu` class
Hub-side menu shell that lets the user pick and run one of several functions via the hub's buttons. Key conventions enforced by this class:

- **Stop-button swap**: while the menu is showing, the system stop button is set to `Button.BLUETOOTH` so `CENTER` is free to mean "select". When a menu item runs, the stop button is moved to `CENTER` so the user can interrupt it; on exit it is restored to `BLUETOOTH`. Anything that calls `hub.system.set_stop_button` inside a menu item will fight this and must restore it.
- **Interrupt is a `SystemExit`**: pressing the (current) stop button raises `SystemExit` inside the running item. `_execute_current_function` catches this, beeps the speaker for 1ms to silence any in-progress beep, and returns to the menu. Other exceptions blink red and re-raise.
- Menu item `function` callables receive the menu's `context` as their only argument (the `Robot` in this repo); if no context was given, the `hub` is passed instead.
- `display` accepts `int` (0–99), single-character `str`, or a 5-row list-of-strings pattern; rendering is delegated to `pix_display.display_content`.

### `pix_display.py` — 5×5 light-matrix rendering
Helpers for drawing on the hub's 5×5 display.

- `display_pattern(hub, pattern)`: `pattern` is exactly 5 strings of length 5. `' '` or `'0'` = off; digits `'1'`–`'9'` = brightness × 10; anything else = 100.
- `display_number(hub, n)` for 0–99: 0–9 use the built-in single-char glyph, 10–19 use hand-drawn patterns from `Patterns.numbers`, 20+ use the built-in scrolling number renderer.
- `Patterns.numbers` only goes up to index 19 — do not index past it.

## Pybricks/MicroPython gotchas

- `from typing import ...` is wrapped in `try/except ImportError` because the hub's MicroPython has no `typing` module at runtime — type hints are for the host-side editor only. Preserve this pattern when adding modules.
- Only import from `pybricks.*`. Standard-library modules beyond what Pybricks ships will `ImportError` on the hub.
- Button polling uses `hub.buttons.pressed()` returning a set; debounce by waiting for release (see `Menu._wait_for_release`) before treating the next press as new.
- `wait(ms)` from `pybricks.tools` is the only sleep — do not use `time.sleep`.
- No `dataclasses`, limited `collections` — plain classes and dicts only.
