# Floorball Shot Plotter V3 Roadmap

This document tracks the ongoing refactor work and the agreed direction for future cleanup.

## Workflow

- Work directly on `main`.
- Before larger refactors, create a flat backup branch, for example `backup-main-before-controls-split`.
- Keep changes small, focused, and behavior-preserving unless a functionality change is discussed first.
- After each code change, pull and test locally before continuing.
- Prefer simple helper extraction and clearer module boundaries over broad architectural rewrites.

## Completed Phases

### Phase 1 - Video runtime cleanup

Status: complete.

Completed work:

- Video runtime logic split out.
- Segment playback behavior fixed:
  - Loop ON loops between Start and Stop.
  - Loop OFF pauses cleanly at Stop.
- Video looping issues resolved.

### Phase 2 - Video overlay separation

Status: complete.

Completed work:

- Video overlay logic extracted into its own module.
- Video overlay responsibilities separated from the rest of the GUI code.

### Phase 3 - Video player cleanup

Status: complete.

Completed work:

- Video player styling extracted into `utils/video_player_style.py`.
- Video player responsibilities reduced.

### Phase 4 - Split `gui/controls.py`

Status: complete.

Completed work:

- `gui/controls.py` now acts as a small orchestrator.
- Control panel sections are split into `gui/panels/controls/` modules.

### Phase 5 - GUI/module cleanup

Status: in progress.

Completed so far:

- Cleaned `gui/panels/controls/heatmap_controls.py`.
- Cleaned `gui/panels/controls/match_controls.py`.
- Cleaned `gui/panels/controls/stats_controls.py`.
- Cleaned `gui/panels/controls/period_controls.py`.
- Cleaned `gui/shotlog_view.py`.
- Cleaned `gui/panels/center_plot.py`.
- Cleaned `gui/layout.py`.
- Cleaned `core/app_bootstrap.py`.
- Cleaned `gui/plot_rendering.py`.
- Cleaned `gui/shotlog_interactions.py`.
- Cleaned `core/app_refresh.py`.
- Cleaned `core/init_state.py`.
- Cleaned `core/demo.py`.
- Cleaned `core/filtering.py`.
- Cleaned `core/event_logic.py`.
- Cleaned `core/core_stats.py`.
- Cleaned `data/match_store.py`.
- Cleaned `data/entry_serialization.py`.
- Cleaned `data/csv_store.py`.
- Cleaned `core/xg.py`.

Regression fixes completed during Phase 5:

- Fixed Remove Nearest so it removes the point nearest the mouse pointer over the rink/canvas instead of falling back to the latest plotted point.
- Added `gui/point_removal.py` for pointer-based point removal.
- Routed both canvas and global Space bindings through the pointer-based removal helper.
- Restored the trash icon on the Delete This Match button.
- Fixed assisted goals so they can ask for and store pass origin points like shots.
- Added event-aware pass-origin and plot-click helpers.

Current backup branches for this cleanup work:

- `backup-main-before-heatmap-controls-cleanup`
- `backup-main-before-event-dialogs-cleanup`

## Current Stable Point

The app has been tested locally after the Phase 5 cleanup and regression fixes.

Confirmed working:

- Controls panel sections.
- Heatmap settings.
- Match manager buttons.
- Period controls.
- View mode dropdown.
- Shot Log display and interactions.
- Center plot click behavior.
- Space / Remove Nearest behavior.
- Trash icon display.
- Menu and startup behavior.
- Shot and goal creation.
- Goal pass-origin flow.
- Save/load match behavior.
- CSV import/export.

## Recommended Next Steps

### 1. Pause and preserve current stable state

Before continuing with more cleanup, optionally create a fresh flat backup branch from the current `main`, for example:

```bash
git checkout main
git pull
git branch backup-main-after-phase5-core-data-cleanup
```

Or create the branch remotely before starting the next larger cleanup batch.

### 2. Continue Phase 5 with remaining GUI modules

Potential next targets:

- `gui/events/event_dialogs.py`
  - Large dialog/options module.
  - Candidate for splitting option data, popup helpers, and dialog flow.
  - This should be done carefully because it affects shot/goal creation.
  - Note: direct option-data extraction has been blocked by the GitHub connector payload filter, so prefer smaller helper modules or local/manual refactor later.

- `gui/plot_interactions.py`
  - Hover/highlight/pass-arrow/remove behavior is sensitive.
  - Avoid broad rewrites unless needed.

### 3. Consider Phase 6 only after Phase 5 settles

Phase 6 would evaluate whether a cleaner service layer is worthwhile.

Do not start this unless there is a clear benefit, such as:

- reducing coupling between GUI and match data,
- making save/load easier to test,
- isolating business logic from Tkinter callbacks.

Possible future service candidates:

- Match service.
- Shot/event service.
- Video link service.
- Statistics/xG service.

## Future Feature: Trained / Custom xG Model

Status: planned, not started.

Goal:

- Build a better xG model from saved Shot Plotter games instead of relying only on the current rule-based zone model in `core/xg.py`.
- Use historical saved shots and goals as training data.
- Keep the current rule-based xG model as a safe fallback.

Important model change:

- A real xG model should predict xG for both saved shots and goals.
- Goals should not automatically be treated as `xG = 1.0` in the trained model.
- Example: a low-quality shot that becomes a goal could still have `xG = 0.04`; a dangerous saved shot could have `xG = 0.60`.

Suggested training features:

- Shot X/Y location.
- Distance to goal.
- Shot angle to goal.
- Shot type.
- Situation.
- Phase.
- Shooter stick hand.
- Passer stick hand.
- Pass origin location when available.
- Pass distance / pass angle when available.
- Period.

Suggested implementation phases:

### xG Phase A - Data preparation

- Create a new module such as `core/xg_model.py`.
- Read all saved match JSON files from the matches folder.
- Convert events into training rows.
- Target value:
  - goal = 1
  - saved shot = 0

### xG Phase B - Model training

- Start with a simple model first, such as logistic regression.
- Keep dependencies minimal and discuss before adding new packages such as scikit-learn.
- Save the trained model to disk so it can be reused.

### xG Phase C - Prediction fallback

- Add `predict_xg(...)` that uses the trained model when available.
- Fall back to the current rule-based `get_xg_value(...)` when no trained model exists.

### xG Phase D - Recalculate existing matches

- Add a safe way to recalculate xG for the current match or all loaded matches.
- Avoid overwriting historical data without confirmation.
- Consider creating backups before bulk recalculation.

### xG Phase E - UI integration

Potential UI actions:

- `Train xG Model from Saved Matches`
- `Recalculate xG for Current Match`
- `Recalculate xG for Loaded Season`
- `Show xG Model Status`

Acceptance criteria:

- Existing rule-based xG still works if no trained model exists.
- Training does not change match data unless the user explicitly recalculates xG.
- Saved matches remain loadable with older app versions where practical.
- xG recalculation can be tested on a copied/backup match first.

## Notes for Next Session

Start by confirming the latest `main` still works locally.

Suggested first next action:

1. Create a fresh backup branch from current `main`.
2. Continue Phase 5 only if there are still clear cleanup wins.
3. Otherwise discuss whether to start the trained xG model feature.
4. For xG work, begin with data extraction and model-design scaffolding before changing event creation.
