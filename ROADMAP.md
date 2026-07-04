# Floorball Shot Plotter V3 Roadmap

This document tracks the completed refactor work and the agreed direction for future feature development.

## Workflow

- Work directly on `main` for normal cleanup and small feature changes.
- Before larger refactors or behavior changes, create a flat backup branch, for example `backup-main-before-feature-name`.
- Prefer broad but themed batches: inspect a wider file group first, then make a safe grouped change, then pull/test once at the end.
- Keep refactor changes behavior-preserving unless a functionality change is discussed first.
- Avoid broad rewrites of sensitive working modules unless there is a bug or clear feature need.

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
- VLC runtime helpers extracted into `utils/video_runtime.py`.
- Overlay creation extracted into `utils/video_overlay.py`.

### Phase 4 - Split `gui/controls.py`

Status: complete.

Completed work:

- `gui/controls.py` now acts as a small orchestrator.
- Control panel sections are split into `gui/panels/controls/` modules.
- Left, center, and right panels have clearer module boundaries.

### Phase 5 - Major GUI/core/data cleanup

Status: complete / stabilized.

Completed work:

- Cleaned and split control-panel setup modules.
- Cleaned layout and panel setup helpers.
- Cleaned Shot Log view and Shot Log interaction helpers.
- Cleaned plot rendering refresh helpers.
- Cleaned app refresh helpers.
- Cleaned app startup/initial-state helpers.
- Cleaned core stats calculations.
- Cleaned demo generation helpers.
- Cleaned match-store save/load dialog helpers.
- Cleaned entry schema/helpers and serialization helpers.
- Cleaned assets/path/export/video-runtime helpers.
- Cleaned video overlay and video button style helpers.
- Cleaned plot-click, event-finalize, popup-positioning, and pass-origin helpers.

Regression fixes completed during Phase 5:

- Fixed Remove Nearest so it removes the point nearest the mouse pointer over the rink/canvas instead of falling back to the latest plotted point.
- Added `gui/point_removal.py` for pointer-based point removal.
- Routed both canvas and global Space bindings through the pointer-based removal helper.
- Restored the trash icon on the Delete This Match button.
- Fixed assisted goals so they can ask for and store pass origin points like shots.
- Added event-aware pass-origin and plot-click helpers.

Confirmed working after the major refactor:

- App startup.
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
- Video overlay open/close behavior.
- Save/load match behavior.
- CSV import/export.
- Demo shot generation.
- Stats and expected-goals panels.

## Current Stable Point

The app is now considered stable after the major refactor. Feature development can resume.

Stable branch to preserve this point:

```text
stable-after-major-refactor
```

Use this stable branch as a known-good rollback point before larger future feature work.

## Sensitive Files To Avoid Unless Needed

The following files are working and should not be broadly rewritten unless there is a bug or a clear feature need:

- `gui/point_removal.py`
- `gui/events/event_dialogs.py`
- `utils/videoplayer.py`
- `core/event_logic.py`
- `core/app_match_actions.py`

Reason:

- These files control deletion, dialog flow, event creation, video playback, or match state.
- Some broad rewrites were blocked by the connector payload filter.
- The cleanup benefit is now smaller than the regression risk.

## Recommended Next Steps

### 1. Start feature development

Good feature candidates:

- UI improvements.
- Better match/season workflow.
- Shot filtering improvements.
- Export/report features.
- Video workflow improvements.
- Quality-of-life fixes discovered during testing.

### 2. Use backup branches for bigger changes

Before any bigger feature branch or behavior change, create a flat backup branch from the current working `main`, for example:

```bash
git checkout main
git pull
git branch backup-main-before-feature-name
```

Or create the backup branch remotely before starting the next larger work batch.

### 3. Consider Phase 6 only if it becomes useful

Phase 6 would evaluate whether a cleaner service layer is worthwhile.

Do not start this automatically. Only consider it if there is a clear benefit, such as:

- reducing coupling between GUI and match data,
- making save/load easier to test,
- isolating business logic from Tkinter callbacks,
- supporting a bigger new feature safely.

Possible future service candidates:

- Match service.
- Shot/event service.
- Video link service.
- Statistics/xG service.

## Future Feature: Trained / Custom xG Model

Status: planned, low priority, parked until Daniel explicitly asks for it.

Goal:

- Build a better xG model from saved Shot Plotter games instead of relying only on the current rule-based zone model in `core/xg.py`.
- Use historical saved shots and goals as training data.
- Keep the current rule-based xG model as a safe fallback.

Priority note:

- Do not start xG model scaffolding, dependency changes, UI changes, or event-creation changes unless Daniel explicitly asks to resume xG work.
- Keep this section as a future reference item only.

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

Start from the stable post-refactor state and switch to feature development unless Daniel asks for more cleanup.

Suggested first next action:

1. Confirm latest `main` still works locally.
2. Pick the next feature or behavior improvement.
3. Create a backup branch before larger feature work.
4. Do not start trained/custom xG model work unless Daniel explicitly asks to resume it.
