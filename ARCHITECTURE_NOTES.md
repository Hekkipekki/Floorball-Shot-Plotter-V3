# Floorball Shot Plotter – Architecture Notes

## Overview

The application follows a modular structure separating:

* application control
* core logic
* data persistence
* GUI rendering
* utilities

---

## Application Layer (App)

Responsible for coordinating the app lifecycle and user actions.

* `core/app_controller.py` → main application class and state
* `core/app_bootstrap.py` → initialization (window, paths, icons, bindings)
* `core/app_match_actions.py` → match-level actions (load/save/delete)
* `app_paths.py` → centralized path management

---

## Core Logic

Pure logic, no UI dependencies.

* `core/schema.py` → entry structure (index constants)
* `core/event_logic.py` → add shot/goal events
* `core/filtering.py` → filtered entry retrieval
* `core/core_stats.py` → stats, xG calculations, heatmap configuration

---

## Data Layer

Handles persistence and file operations.

* `data/match_store.py` → match save/load/delete
* `data/entry_serialization.py` → JSON-safe conversion
* `data/csv_store.py` → CSV import/export

---

## GUI Layer

### Shot Log

* `gui/shotlog_view.py` → Treeview rendering
* `gui/shotlog_interactions.py` → hover, delete, sync
* `gui/shotlog_video.py` → video linking & playback
* `gui/shotlog.py` → wrapper (legacy compatibility)

### Plot

* `gui/plot_background.py` → background loading
* `gui/plot_rendering.py` → plot drawing & heatmap
* `gui/plot_interactions.py` → hover, click, remove
* `gui/plot_controller.py` → wrapper (legacy compatibility)

---

## Utilities

Reusable helpers across modules.

* `utils/helpers.py` → general helpers
* `utils/tooltips.py` → tooltip handling
* `utils/videoplayer.py` → embedded VLC player

---

## Data & Assets

* `data/` → runtime data (matches, exports, videos)
  (ignored in Git)
* `assets/` → static resources (icons, images)

---

## Notes

* Always use constants from `core/schema.py` (no raw indexes)
* All file paths must go through `app_paths.py`
* GUI modules should not contain business logic
* Data layer should not depend on GUI

---

## Known Technical Debt

* `core/core_stats.py` handles multiple responsibilities and may be split later
* `gui/shotlog.py` and `gui/plot_controller.py` exist for compatibility and may be removed
* Video system can be further decoupled from GUI
