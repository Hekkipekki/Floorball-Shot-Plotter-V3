from __future__ import annotations

import math

from core.entry_helpers import get_number
from gui.plot_rendering import get_visible_entries, safe_get_xy


def _pointer_display_position(app):
    try:
        canvas_widget = app.canvas.get_tk_widget()
        pointer_x, pointer_y = app.root.winfo_pointerxy()
        canvas_x = pointer_x - canvas_widget.winfo_rootx()
        canvas_y = pointer_y - canvas_widget.winfo_rooty()

        if canvas_x < 0 or canvas_y < 0:
            return None
        if canvas_x > canvas_widget.winfo_width() or canvas_y > canvas_widget.winfo_height():
            return None

        display_y = canvas_widget.winfo_height() - canvas_y
        if not app.ax.bbox.contains(canvas_x, display_y):
            return None

        return canvas_x, display_y
    except Exception:
        return None


def _nearest_visible_index(app, entries):
    pointer_position = _pointer_display_position(app)
    if pointer_position is None:
        return None

    pointer_x, pointer_y = pointer_position
    best_distance = None
    best_index = None

    for index, entry in enumerate(entries):
        x, y = safe_get_xy(entry)
        if x is None:
            continue

        display_x, display_y = app.ax.transData.transform((x, y))
        distance = math.hypot(display_x - pointer_x, display_y - pointer_y)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_index = index

    return best_index


def _master_entry_index(app, entry):
    current_match = app.current_match.get()
    if current_match in ("All", "Season"):
        return None

    entry_number = get_number(entry)
    for index, candidate in enumerate(app.match_logs.get(current_match, [])):
        if get_number(candidate) == entry_number:
            return index

    return None


def remove_nearest_point(app, event=None):
    if getattr(app, "view_mode", None) and app.view_mode.get() != "Plot":
        return

    entries = get_visible_entries(app)
    if not entries:
        return

    target_index = _nearest_visible_index(app, entries)

    if target_index is None:
        hover_index = getattr(app, "_hover_index", None)
        if hover_index is not None and 0 <= hover_index < len(entries):
            target_index = hover_index

    if target_index is None or not (0 <= target_index < len(entries)):
        return

    current_match = app.current_match.get()
    if current_match in ("All", "Season"):
        return

    master_index = _master_entry_index(app, entries[target_index])
    if master_index is None:
        return

    del app.match_logs[current_match][master_index]
    app.update_log_view_and_stats()

    try:
        app.auto_update_current_match()
    except Exception:
        pass
