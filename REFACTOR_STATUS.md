# Refactor Status

Status: major refactor complete and stabilized.

This file summarizes the current codebase state after the large cleanup/refactor sequence.

## Current State

The app has been tested after the major cleanup batches and is ready for normal feature development again.

Confirmed working areas:

- App startup.
- Controls panel.
- Period and view-mode controls.
- Heatmap controls.
- Stats and expected-goals panels.
- Shot Log display, hover, delete, and video menu interactions.
- Plot click shot/goal creation.
- Assisted shot/goal pass-origin flow.
- Video overlay open/close flow.
- Match save/load.
- CSV import/export.
- Demo shot generation.

## Stable Branch

Create or use this branch as the stable rollback point after the major refactor:

```text
stable-after-major-refactor
```

## Refactor Policy Going Forward

Use feature-focused changes now. Do not continue broad cleanup just for tidiness.

Before larger feature or behavior changes:

1. Create a flat backup branch from `main`.
2. Make the change in a focused batch.
3. Pull and test locally.
4. Keep behavior changes explicit.

## Sensitive Files

Avoid broad rewrites unless there is a bug or a strong feature reason:

- `gui/point_removal.py`
- `gui/events/event_dialogs.py`
- `utils/videoplayer.py`
- `core/event_logic.py`
- `core/app_match_actions.py`

These files are behavior-sensitive and currently working.

## Parked Work

The trained/custom xG model is parked until Daniel explicitly asks to resume it.

Do not start xG model scaffolding, dependency changes, UI changes, or event-creation changes unless requested.

## Recommended Next Step

Pick the next actual feature or behavior improvement and develop it from the stable post-refactor state.
