from __future__ import annotations

import math
import numpy as np
from matplotlib.patches import FancyArrowPatch

from core.entry_helpers import (
    get_number,
    get_passer,
    get_pass_xy,
    get_result,
    get_shooter,
)
from gui.constants import (
    HIGHLIGHT_GOAL_EDGE,
    HIGHLIGHT_GOAL_FACE,
    HIGHLIGHT_GOAL_LINEWIDTH,
    HIGHLIGHT_GOAL_SIZE,
    HIGHLIGHT_PASS_EDGE,
    HIGHLIGHT_PASS_LINEWIDTH,
    HIGHLIGHT_PASS_SIZE,
    HIGHLIGHT_PASS_FACE,
    HIGHLIGHT_PASSER_BBOX_EC,
    HIGHLIGHT_PASSER_TEXT_COLOR,
    HIGHLIGHT_SHOOTER_BBOX_EC,
    HIGHLIGHT_SHOOTER_TEXT_COLOR,
    HIGHLIGHT_SHOT_EDGE,
    HIGHLIGHT_SHOT_FACE,
    HIGHLIGHT_SHOT_LINEWIDTH,
    HIGHLIGHT_SHOT_SIZE,
    HIGHLIGHT_TEXT_BBOX_ALPHA,
    HIGHLIGHT_TEXT_BBOX_FC,
    HIGHLIGHT_TEXT_FONT_SIZE,
    HIGHLIGHT_TEXT_X_OFFSET,
    HIGHLIGHT_TEXT_Y_OFFSET,
    HOVER_DISTANCE_THRESHOLD_PX,
    PASS_ARROW_COLOR,
    PASS_ARROW_LINEWIDTH,
    PASS_ARROW_MUTATION_SCALE,
    PASS_ARROW_OFFSET,
    PASS_ARROW_ZORDER,
    PLOT_DEFAULT_XLIM,
    PLOT_DEFAULT_YLIM,
)
from gui.plot_rendering import get_visible_entries, safe_get_xy, redraw_background, update_plot


def draw_pass_arrow(ax, pass_x, pass_y, shot_x, shot_y, offset=PASS_ARROW_OFFSET):
    dx = shot_x - pass_x
    dy = shot_y - pass_y
    distance = math.hypot(dx, dy)

    if distance <= offset or distance == 0:
        end_x, end_y = shot_x, shot_y
    else:
        ratio = (distance - offset) / distance
        end_x = pass_x + dx * ratio
        end_y = pass_y + dy * ratio

    arrow = FancyArrowPatch(
        (pass_x, pass_y),
        (end_x, end_y),
        arrowstyle="->",
        color=PASS_ARROW_COLOR,
        linewidth=PASS_ARROW_LINEWIDTH,
        mutation_scale=PASS_ARROW_MUTATION_SCALE,
        zorder=PASS_ARROW_ZORDER,
    )
    ax.add_patch(arrow)
    return arrow


def highlight_point(app, index):
    view = app.view_mode.get() if hasattr(app, "view_mode") else "Plot"
    if view in ("Heatmap", "Goal Heatmap", "Save Heatmap"):
        return

    entries = get_visible_entries(app)
    if not (0 <= index < len(entries)):
        return

    entry = entries[index]
    x, y = safe_get_xy(entry)
    if x is None:
        return

    app.ax.cla()
    redraw_background(app)

    app.highlighted = []

    passer = get_passer(entry) or ""
    shooter = get_shooter(entry) or ""

    if get_result(entry) == "G":
        shot = app.ax.scatter(
            x, y,
            s=HIGHLIGHT_GOAL_SIZE,
            c=HIGHLIGHT_GOAL_FACE,
            edgecolors=HIGHLIGHT_GOAL_EDGE,
            linewidths=HIGHLIGHT_GOAL_LINEWIDTH,
            zorder=10,
        )
    else:
        shot = app.ax.scatter(
            x, y,
            s=HIGHLIGHT_SHOT_SIZE,
            edgecolors=HIGHLIGHT_SHOT_EDGE,
            facecolors=HIGHLIGHT_SHOT_FACE,
            linewidths=HIGHLIGHT_SHOT_LINEWIDTH,
            zorder=10,
        )
    app.highlighted.append(shot)

    if shooter in ("Left", "Right"):
        txt = app.ax.text(
            x + HIGHLIGHT_TEXT_X_OFFSET,
            y + HIGHLIGHT_TEXT_Y_OFFSET,
            f"S: {shooter}",
            color=HIGHLIGHT_SHOOTER_TEXT_COLOR,
            fontsize=HIGHLIGHT_TEXT_FONT_SIZE,
            weight="bold",
            zorder=11,
            bbox=dict(
                boxstyle="round,pad=0.2",
                fc=HIGHLIGHT_TEXT_BBOX_FC,
                ec=HIGHLIGHT_SHOOTER_BBOX_EC,
                alpha=HIGHLIGHT_TEXT_BBOX_ALPHA,
            ),
        )
        app.highlighted.append(txt)

    pass_x, pass_y = get_pass_xy(entry)

    if pass_x is not None and pass_y is not None:
        p = app.ax.scatter(
            pass_x, pass_y,
            s=HIGHLIGHT_PASS_SIZE,
            c=HIGHLIGHT_PASS_FACE,
            edgecolors=HIGHLIGHT_PASS_EDGE,
            linewidths=HIGHLIGHT_PASS_LINEWIDTH,
            zorder=9,
        )
        app.highlighted.append(p)

        arr = draw_pass_arrow(app.ax, pass_x, pass_y, x, y)
        app.highlighted.append(arr)

        if passer in ("Left", "Right"):
            txt = app.ax.text(
                pass_x + HIGHLIGHT_TEXT_X_OFFSET,
                pass_y + HIGHLIGHT_TEXT_Y_OFFSET,
                f"P: {passer}",
                color=HIGHLIGHT_PASSER_TEXT_COLOR,
                fontsize=HIGHLIGHT_TEXT_FONT_SIZE,
                weight="bold",
                zorder=11,
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    fc=HIGHLIGHT_TEXT_BBOX_FC,
                    ec=HIGHLIGHT_PASSER_BBOX_EC,
                    alpha=HIGHLIGHT_TEXT_BBOX_ALPHA,
                ),
            )
            app.highlighted.append(txt)

    app.ax.set_xlim(getattr(app, "original_xlim", PLOT_DEFAULT_XLIM))
    app.ax.set_ylim(getattr(app, "original_ylim", PLOT_DEFAULT_YLIM))
    app.ax.axis("off")

    app.is_hover_preview = True
    app.canvas.draw_idle()


def clear_highlight(app):
    if getattr(app, "is_hover_preview", False):
        update_plot(app)
        app.is_hover_preview = False


def connect_hover_events(app):
    if getattr(app, "_hover_connected", False):
        return
    app._hover_connected = True

    def on_motion(event):
        if app.view_mode.get() != "Plot":
            return
        if not event.inaxes or event.x is None or event.y is None:
            return

        entries = get_visible_entries(app)
        if not entries:
            return

        found_index = None

        for idx, entry in enumerate(entries):
            x, y = safe_get_xy(entry)
            if x is None:
                continue
            disp_x, disp_y = app.ax.transData.transform((x, y))
            dist = np.hypot(disp_x - event.x, disp_y - event.y)
            if dist < HOVER_DISTANCE_THRESHOLD_PX:
                found_index = idx
                break

        if found_index is not None:
            app._hover_index = found_index
            highlight_point(app, found_index)
        else:
            app._hover_index = None
            clear_highlight(app)

    def on_click(event):
        if not event.inaxes or event.xdata is None or event.ydata is None:
            return
        try:
            app._last_rink_click = (float(event.xdata), float(event.ydata))
        except Exception:
            app._last_rink_click = None

        try:
            app.root.focus_set()
        except Exception:
            pass

    app.canvas.mpl_connect("motion_notify_event", on_motion)
    app.canvas.mpl_connect("button_press_event", on_click)


def _find_master_entry_index(app, entry):
    current_match = app.current_match.get()
    if current_match in ("All", "Season"):
        return None

    match_entries = app.match_logs.get(current_match, [])
    entry_number = get_number(entry)

    for i, candidate in enumerate(match_entries):
        if get_number(candidate) == entry_number:
            return i
    return None


def remove_nearest_point(app, event=None):
    if getattr(app, "view_mode", None) and app.view_mode.get() != "Plot":
        return

    entries = get_visible_entries(app)
    if not entries:
        return

    target_index = None

    hover_index = getattr(app, "_hover_index", None)
    if hover_index is not None and 0 <= hover_index < len(entries):
        target_index = hover_index
    else:
        last_click = getattr(app, "_last_rink_click", None)
        if last_click is not None:
            cx, cy = last_click
            best_dist = None
            best_idx = None

            for idx, entry in enumerate(entries):
                x, y = safe_get_xy(entry)
                if x is None:
                    continue
                d = math.hypot(x - cx, y - cy)
                if best_dist is None or d < best_dist:
                    best_dist = d
                    best_idx = idx

            target_index = best_idx
        else:
            target_index = len(entries) - 1

    if target_index is None or not (0 <= target_index < len(entries)):
        return

    current_match = app.current_match.get()

    if current_match in ("All", "Season"):
        return

    target_entry = entries[target_index]
    master_index = _find_master_entry_index(app, target_entry)
    if master_index is None:
        return

    del app.match_logs[current_match][master_index]
    app.update_log_view_and_stats()

    try:
        app.auto_update_current_match()
    except Exception:
        pass