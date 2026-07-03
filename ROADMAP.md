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

Regression fixes completed during Phase 5:

- Fixed Remove Nearest so it removes the point nearest the mouse pointer over the rink/canvas instead of falling back to the latest plotted point.
- Added `gui/point_removal.py` for pointer-based point removal.
- Routed both canvas and global Space bindings through the pointer-based removal helper.
- Restored the trash icon on the Delete This Match button.

Current backup branch for this cleanup batch:

- `backup-main-before-heatmap-controls-cleanup`

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

## Recommended Next Steps

### 1. Pause and preserve current stable state

Before continuing with more cleanup, optionally create a fresh flat backup branch from the current `main`, for example:

```bash
git checkout main
git pull
git branch backup-main-after-phase5-gui-cleanup
```

Or create the branch remotely before starting the next larger cleanup batch.

### 2. Continue Phase 5 with remaining GUI modules

Potential next targets:

- `gui/events/event_dialogs.py`
  - Large dialog/options module.
  - Candidate for splitting option data, popup helpers, and dialog flow.
  - This should be done carefully because it affects shot/goal creation.

- `gui/plot_rendering.py`
  - Likely behavior-heavy.
  - Candidate for small helper extraction only after careful inspection.

- `gui/plot_interactions.py`
  - Hover/highlight/pass-arrow/remove behavior is sensitive.
  - Avoid broad rewrites unless needed.

- `gui/shotlog_interactions.py`
  - Small but behavior-sensitive.
  - Possible cleanup around delete/update helpers.

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

## Notes for Next Session

Start by confirming the latest `main` still works locally.

Suggested first next action:

1. Create a fresh backup branch from current `main`.
2. Inspect `gui/events/event_dialogs.py`.
3. Propose a split plan before changing it.
4. Keep the first change small, such as moving static option dictionaries into a dedicated module.
