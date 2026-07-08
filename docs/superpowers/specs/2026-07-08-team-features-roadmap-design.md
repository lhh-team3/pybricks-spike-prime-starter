# Pybricks Git — Team Features Roadmap
Menu manager · robot-setup templates · protected upstream files

## Context

FLL teams fork `pybricks-spike-prime-starter` and use the `pybricks-git-extension` to sync `.py` files between their fork and code.pybricks.com. Today the starter is plain-Python-only (missions hand-registered in `main.py`, config centralized in `robot.py`), but real teams work in **block programs**, which change the rules: block files can't import sibling modules (so every block program inlines its own device setup), and importing a block file *executes* it. The extension has no in-page UI beyond two toolbar buttons and no notion of file ownership, so team edits to upstream files (menu.py, pix_display.py) create GitHub sync-fork conflicts.

Goal: make the menu, robot config, and upstream-update workflows work for block-based teams — menu slots managed by drag-and-drop instead of hand-editing main.py, robot setup defined once in a team-owned template block program and propagated to all programs, and upstream framework files self-healing so "Sync fork" + Pull always works.

**Repos touched:** `pybricks-spike-prime-starter` (phase 1) and `pybricks-git-extension` (phases 2–4).

## Decisions made with Brendon

1. **Menu slots support both kinds**: whole-program items (import = run, the official hub_menu pattern) and method items (a named function from a module whose top level is setup-only).
2. **Gesture surface**: floating manager panel is primary + right-click/long-press context menu on the page's file list. No Blockly-workspace hooks.
3. **Read-only = git-layer + badges**: edits to protected files are never committed and are overwritten on pull (with a visible warning); no Monaco/Blockly enforcement.
4. **Setup propagation = full JSON splice, safety-first**: heavily-tested splicer module, only touches recognizable setup chains, auto-commits a snapshot first, skips-and-reports anything uncertain.
5. **Sequence**: (1) template repo v2 → (2) protected files → (3) menu manager UI → (4) template-on-new + setup propagation. Phase 1 implemented now.

---

## The cross-phase contract

These three artifacts are defined in phase 1 and coded against by phases 2–4.

### `menu_config.py` (team-owned; extension-regenerated in phase 3)

File = optional docstring/comments + exactly one top-level `MENU_ITEMS = [<dict literals>]`. Values limited to int/str/bool/None/list-of-str (machine-parseable via `ast.literal_eval` semantics; the extension rewrites the whole file from its own template — comments inside the list are not preserved).

```python
MENU_ITEMS = [
    {"display": 1, "module": "mission_01_go_out_and_turn", "function": "run"},
    # Whole program (blocks or Python) — picking it runs the entire file:
    # {"display": 3, "module": "my_blocks_program"},
    # One My Block from a blocks file (called with no robot argument):
    # {"display": 4, "module": "arm_moves", "function": "lift_arm", "blocks": True},
]
```

- `display` (required): int 0–99, 1-char str, or list of exactly 5 pattern strings.
- `module` (required): bare module name, no dots.
- `function` (optional): absent/None = whole-program item (import runs it).
- `blocks` (optional, default False): call with no args; if result is awaitable, drive with `run_task`. Otherwise `fn(robot)` (existing plain-Python convention).
- `enabled` (optional, default True): disabled items skipped at load, kept in file.
- List order = menu order.

### `.pybricks-git.json` (repo root; read by extension from the git tree, never synced into the editor — `.py` filter keeps it out)

```json
{
  "schemaVersion": 1,
  "menuConfig": "menu_config.py",
  "setupTemplate": "robot_setup_template.py",
  "teamSetup": "robot_setup.py",
  "protected": [".pybricks-git.json", "main.py", "menu.py", "pix_display.py",
                "mission_template.py", "robot_setup_template.py", "check_project.py"]
}
```

`robot.py`, `menu_config.py`, sample missions, and the team's `robot_setup.py` are intentionally NOT protected. Unknown keys ignored; `schemaVersion` gates parsing.

### Setup-file convention

A setup file is a blocks file whose workspace JSON contains **only** the non-deletable `blockGlobalSetup` chain (no main-program blocks; generated Python has no `run_task` and no trailing statements). `setupTemplate` = protected upstream example; `teamSetup` = team-owned copy the splice phase uses as the source of truth.

---

## Phase 1 — Template repo v2 (implement now)

In `/home/brendon/code/github/lansingtechstudio/pybricks-spike-prime-starter`:

**New `menu_config.py`** — as above, seeded with the two existing missions, with a kid-facing docstring explaining each key and "the extension can rewrite this file".

**Rewrite `main.py`** — thin loader over `menu_config.py`:
- `_import_fresh(name)`: `del sys.modules[name]` (via `usys`/`sys` fallback) before `__import__` so whole-program items are re-runnable, including after a CENTER interrupt (partial module left cached).
- `_make_runner(item)`: closure dispatching the three call shapes — whole-program (`_import_fresh`), `blocks: True` (no-arg call; `run_task(result)` if result has `.send`), plain (`fn(robot)`). Method-item modules import once and stay cached (no device re-construction per run).
- Lazy `Robot()`: only constructed if some enabled item is a plain (non-blocks) function item — an all-blocks team never claims ports via robot.py defaults.
- Broken config entries → printed skip message, rest of menu loads; zero items → Menu's existing `?` display.

**`menu.py`** — no functional changes; docstring updates only (runners may wrap imports/async calls; whole-program items run under the CENTER stop button — existing swap/SystemExit/auto_increment behavior applies for free).

**New `.pybricks-git.json`** — as above.

**New `robot_setup_template.py`** — authored **in code.pybricks.com** (line-1 JSON and Python must match; never hand-write): blockGlobalSetup chain only, mirroring robot.py defaults (ports A/B, 56 mm wheel, 114 mm axle track, one attachment). Structural reference: `pybricks-demo/blocks.py` lines 1–13.

**New `check_project.py`** — desktop-only (CPython) verifier: `py_compile` every `.py`; `ast`-parse `menu_config.py` (docstring + single `MENU_ITEMS` literal assignment, full schema validation, every referenced module file exists); validate `.pybricks-git.json` (schema, listed files exist); validate setup files (line-1 sentinel, JSON parses, has `blockGlobalSetup`, no `run_task`).

**Docs** — `mission_template.py` docstring step 3 → "add one line in menu_config.py"; README: rewrite menu/new-mission sections, add "Using block programs" (whole-program vs `blocks: True` items, the `robot_setup.py` convention, why block files can't import robot.py) and "Files you shouldn't edit"; CLAUDE.md: new architecture (loader, contract, manifest, block conventions, double-device-construction gotcha).

**Implementation order**: `.pybricks-git.json` → `menu_config.py` → `main.py` → `mission_template.py` → `check_project.py` (run it) → author `robot_setup_template.py` in the IDE → README/CLAUDE.md → on-hub checklist.

### Phase 1 verification
- `python3 check_project.py` passes.
- On-hub manual checklist (the must-verify items): shipped config runs missions 1–2 with context and auto-advance; CENTER interrupt → back to menu; whole-program block item runs **twice in one session** (verifies `del sys.modules` on Pybricks MicroPython); interrupt-then-rerun; async `blocks: True` item runs via `run_task` from the sync menu and reruns from cached module; sync no-arg blocks function (coroutine detection via `.send`); broken/disabled config entries skip cleanly; all-blocks config never constructs `Robot()`; mixed block-item + plain-mission session on shared ports (record behavior); `usys` fallback works.
- Extension round-trip: pull the updated fork into code.pybricks.com, edit menu_config.py, commit, confirm on GitHub.

### Phase 1 risks
`del sys.modules` unverified on Pybricks firmware (fallback: whole-program items run once per boot; document or exec-based loader later) · coroutine detection via `hasattr(result, "send")` on MicroPython · double device construction when block modules + `Robot()` share ports in one session (mitigated by lazy Robot; documented until phase 4 splice lands).

---

## Phase 2 — Protected upstream files (extension, small)

In `pybricks-git-extension/src/background.js` (engine — keep DI pattern, all testable under `test/`):
- New helper: read `.pybricks-git.json` from the fetched remote head's tree (engine already reads blobs from the tree; parse with schemaVersion guard, tolerate absence → empty protection).
- `pullOp`: return `protected` paths in the response (content.js can warn/badge); pull already overwrites the editor, so restore is free.
- `commitOp`: for protected paths, ignore the editor payload's content and keep the tree's version; when they differ, report them in a `protectedSkipped` list in the response.
- `content.js`: after commit, show a notice when `protectedSkipped` is non-empty ("Your changes to menu.py weren't saved — that file is managed by your coach's repo; Pull to restore it").
- Tests: extend `test/background.test.mjs` fixtures (git-http-server repos gain a manifest) — commit with edited protected file keeps tree version + reports; pull restores; missing/malformed manifest = no-op.

## Phase 3 — Floating menu manager + file-list context menu (extension)

- `src/inject.js`: new bridge ops — `upsert-files` (partial write: update/insert given paths only, preserving `viewState`/`uuid`; unlike `apply-files` it must NOT delete unlisted paths) and reuse `list-files` for reads.
- `src/content.js`:
  - Toolbar toggle button (existing mount pattern) shows/hides the panel.
  - Panel: `position: fixed` on `document.body`, high z-index, inline styles (existing pattern), draggable by header, position persisted in `chrome.storage.local`. Lists menu slots from parsed `menu_config.py` + an "available programs/methods" list from IndexedDB contents.
  - Method eligibility parser (pure function, unit-tested): block files detected by line-1 sentinel; eligible methods = top-level `def`/`async def` names when the file has no top-level `run_task(` call and no trailing main statements.
  - Slot editing: drag to reorder, enable/disable toggle, display editor (number 0–99 / single char / 5×5 brightness grid mirroring pix_display semantics).
  - Save = regenerate `menu_config.py` text from template → `upsert-files`. Decide at implementation whether to `location.reload()` (dexie-observable staleness) or skip when menu_config.py isn't the open file.
  - New `MutationObserver` (doesn't exist today) to find/track the page's file-list DOM; `contextmenu` + long-press (touch) handlers on file rows → "Add to menu" (and "New program from template" in phase 4). Protected files get a badge here too.
- Tests: parser + config generator as pure functions in `test/`; manual E2E via `test/e2e/` recipe.

## Phase 4 — New-program-from-template + setup propagation (extension, riskiest)

- **New program**: panel button (and file-list context menu item) → prompt name → create IndexedDB file seeded from the team's `robot_setup.py` content (mint uuid, `viewState: null`) → reload. Also a passive nudge: when the panel opens, flag block programs whose setup chain differs from the template (no live file-creation hook needed).
- **Splicer**: new `src/blocksplice.js` (classic script, DI/testable like background.js): parse line-1 workspace JSON → locate `blockGlobalSetup` chain → replace with template's chain, remapping Blockly variable IDs by matching variable *names* → rewrite the generated-Python "# Set up all devices." section to match → recompute sha256.
- **Safety rails** (agreed): only touch files whose existing setup chain matches the recognizable shape; auto-commit a snapshot ("Before robot setup update") before propagating so Pull can restore; skip-and-report any file with unmatched variables or unrecognized structure; never touch protected files or the templates.
- **Tests**: fixture-heavy — real workspace JSONs (harvest from pybricks-demo and freshly-authored files) covering variable remap, renamed variables (skip path), extra sensors, and round-trip: spliced file re-opened in code.pybricks.com must load and regenerate identical Python (manual E2E step).

---

## Overall verification

- Phase 1: `check_project.py` + on-hub checklist above; extension pull/commit round-trip against a real fork.
- Phases 2–4: `npm test` (engine + parser + splicer suites, hermetic git server); browser E2E per `test/e2e/` + memory recipe (headless Chromium via CDP); final acceptance = full team workflow on a real fork: sync fork on GitHub → Pull → protected files restored → build menu in panel → new program from template → propagate setup → Commit → verify tree on GitHub.

## Execution model

Fable (this session) acts as orchestrator only: it decomposes each phase into well-scoped tasks, dispatches them to **Opus subagents** (`Agent` tool with `model: "opus"`) that write the actual code, and then **validates every deliverable itself** — reading the diffs, running `check_project.py` / `npm test`, and checking conformance against the contract section above — before moving to the next task. Work that can proceed independently is dispatched in parallel; anything failing validation goes back to a subagent with concrete corrections. Runs in auto mode (no per-step confirmation).

## Step 0 at implementation time

Save this design as `docs/superpowers/specs/2026-07-08-team-features-roadmap-design.md` in the starter repo (plan mode blocked writing it now) and commit it before code changes.
