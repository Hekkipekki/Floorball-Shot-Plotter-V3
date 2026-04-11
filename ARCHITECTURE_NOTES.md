# Floorball Shot Plotter – Architecture Notes

## Entry schema
Entries use tuple/list positions defined in `core/schema.py`.

## Core
- `core/schema.py` → shared entry indexes/constants
- `core/filtering.py` → filtered entry retrieval
- `core/event_logic.py` → add shot/goal event logic
- `core/core_stats.py` → stats, xG display, heatmap presets, refresh orchestration

## Data
- `data/match_store.py` → public match save/load/delete + CSV dialog API
- `data/entry_serialization.py` → JSON-safe serialization/deserialization
- `data/csv_store.py` → CSV read/write

## GUI
### Shot log
- `gui/shotlog_view.py` → treeview setup and rendering
- `gui/shotlog_interactions.py` → hover/delete/master-sync logic
- `gui/shotlog_video.py` → video link/edit/remove/play
- `gui/shotlog.py` → compatibility wrapper

### Plot
- `gui/plot_background.py` → background image loading
- `gui/plot_rendering.py` → update plot, apply sensitivity, apply KDE
- `gui/plot_interactions.py` → hover highlight, remove nearest, click tracking
- `gui/plot_controller.py` → compatibility wrapper

## Utils
- `utils/helpers.py` → shared generic helpers
- `utils/tooltips.py` → tooltip behavior
- `utils/videoplayer.py` → embedded VLC overlay player

## Notes
- `gui/shotlog.py` and `gui/plot_controller.py` are currently thin wrappers kept for compatibility.
- Use constants from `core/schema.py` instead of raw tuple indexes.
- Video metadata is stored as a dict in entry index `IDX_VIDEO`.