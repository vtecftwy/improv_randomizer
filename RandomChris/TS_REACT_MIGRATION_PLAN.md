# TS + React migration plan for `RandomChris`

Perfect—I inspected `RandomChris` and can now give you a concrete split + migration plan.

## 1) Codebase split: GUI vs game logic

### GUI module (Tkinter desktop app)
**`RandomChris/gamespace.py`**
- This is the GUI/view/controller layer.
- Handles:
  - Tk window, canvas, layout, styles
  - button callbacks (`click_next`)
  - drawing game bubbles / updating labels
  - sound playback (`playsound`)
  - timer UI (`countdown`)
  - display of selected game, host, players, prompt
- It explicitly says it delegates logic to `session` (`GameSession`), which is good for migration.

### Game logic module (core engine)
**`RandomChris/gamesession.py`**
- This is the logic/state engine.
- Handles:
  - loading games/cast/prompts from config files
  - building game sequence with category constraints (`create_game_sequence`)
  - weighted host/player selection fairness (`compute_probs`, `pick_cast`)
  - session state transitions (`pick_next_game`)
  - timing (`time_left`)
- Contains domain objects:
  - `Game`
  - `Player`

### Shared utilities/config/editors
**`RandomChris/utils.py`**
- Mixed concerns:
  - config loading (`get_config`, `get_paths`) → logic-side infra
  - logging decorators
  - Jupyter widget editors (`WidgetCast`, `WidgetGames`, `WidgetPrompts`) → admin UI tooling, not runtime game loop

### App entrypoint
**`RandomChris/__main__.py`**
- Wires `GameSession + GameSpace`, starts Tk main loop.
- Also reads CLI args for category-priority behavior.

## 2) Can this run as TS + React fully in-browser + local config save?

**Yes.** This project is a good fit.

You can do:
- **Game engine in TypeScript** (port `GameSession`, `Game`, `Player`)
- **UI in React** (replace `GameSpace`)
- **Local persistence**:
  - config + last session: `localStorage`
  - optional stats/history: `IndexedDB`

No server required for core gameplay.
A web server is only needed to **serve static assets** (React build).

## 3) Architecture + plan (specific to this repo)

## Proposed architecture

- `web/src/engine/`
  - `types.ts` (`Game`, `Player`, `SessionState`, `Config`)
  - `session.ts` (port of `GameSession`)
  - `selection.ts` (`computeProbs`, `pickCast`)
  - `sequence.ts` (`createGameSequence`)
- `web/src/ui/`
  - `GameBoard.tsx` (bubble layout rendering)
  - `InfoPanel.tsx` (players/host/prompt)
  - `Controls.tsx` (Start/Next button + timer)
- `web/src/state/`
  - Zustand/Redux store for session state
- `web/src/persistence/`
  - `configStore.ts` (localStorage)
  - `statsStore.ts` (localStorage or IndexedDB)
- `web/public/assets/`
  - background image/audio files

## Migration sequence

1. **Port data model & loaders**
   - Move JSON/text config format into browser-friendly JSON.
   - Replace file reads with bundled JSON + user-editable stored config.

2. **Port engine first (no UI)**
   - `create_game_sequence`
   - `compute_probs`
   - `pick_cast`
   - `pick_next_game`
   - Add unit tests for parity.

3. **React UI implementation**
   - Render game nodes + completed/current state colors.
   - Info panel updates from engine state.
   - Start/Next flow mirrors current behavior.

4. **Timer + audio**
   - Use `setInterval` for countdown.
   - Use `HTMLAudioElement` or the Web Audio API for sound cues.

5. **Config editor page**
   - Replace Jupyter widget tools with React forms/tables.
   - Save config locally and allow reset/export/import JSON.

6. **Validation + parity checks**
   - Compare 20+ sample runs between Python and TS outputs (distribution/fairness behavior, constraints).

## Important porting notes from current code

- There are a few typos/inconsistencies in Python (`host_exlude`, `set-priority-category` vs `set-category-priority`)—clean these during the TS port.
- `gamesession.py` currently does some file-loading at import time; in TS, prefer explicit initialization.
- `gamespace.py` mixes display + stats updates. In React, keep stats updates in the engine/store layer.

## Optional next deliverables

If wanted next:
1. a **file-by-file TS scaffold** for `web/` with starter code signatures, and
2. a **mapping table** for each Python method to its target TS function or component.
