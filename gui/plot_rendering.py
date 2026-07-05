from __future__ import annotations

import tkinter as tk

from core.entry_helpers import get_xy
from gui.constants import PLOT_DEFAULT_XLIM, PLOT_DEFAULT_YLIM
from gui.plotting import plot_points, plot_heatmap
from gui.shot_zone_overlay import load_shot_zone_overlay, shot_zone_overlay_enabled

DEFAULT_VIEW_MODE = "Plot"
HEATMAP_VIEW_MODES = ("Heatmap", "Goal Heatmap", "Save Heatmap")
SLIDER_MIN_VALUE = 0
SLIDER_MAX_VALUE = 1.0


def get_visible_entries(app):
    """
    Always return what the user sees right now.
    Prefer CoreLogic's filtered view if available.
    """
    try:
        if hasattr(app, "logic") and hasattr(app.logic, "get_filtered_entries"):
            return app.logic.get_filtered_entries()
    except Exception:
        pass

    return list(getattr(app, "log_entries", []))


def safe_get_xy(entry):
    return get_xy(entry)


def _background_extent(app):
    return getattr(
        app,
        "img_extent",
        [*PLOT_DEFAULT_XLIM, PLOT_DEFAULT_YLIM[0], PLOT_DEFAULT_YLIM[1]],
    )


def redraw_background(app):
    if getattr(app, "img", None) is not None:
        app.ax.imshow(
            app.img,
            extent=_background_extent(app),
            origin="upper",
            aspect="auto",
        )


def redraw_shot_zone_overlay(app):
    if not shot_zone_overlay_enabled(app):
        return

    overlay = getattr(app, "shot_zone_overlay_img", None)
    if overlay is None:
        overlay = load_shot_zone_overlay(app)
    if overlay is None:
        return

    app.ax.imshow(
        overlay,
        extent=_background_extent(app),
        origin="upper",
        aspect="auto",
        zorder=1,
    )


def _apply_default_axes(app) -> None:
    app.ax.set_xlim(getattr(app, "original_xlim", PLOT_DEFAULT_XLIM))
    app.ax.set_ylim(getattr(app, "original_ylim", PLOT_DEFAULT_YLIM))
    app.ax.axis("off")


def _draw_current_view(app, entries, view: str) -> None:
    if view in HEATMAP_VIEW_MODES:
        plot_heatmap(app, entries, view)
    else:
        plot_points(app, entries)

    app.ax.axis("off")


def _refresh_canvas(app) -> None:
    app.canvas.draw_idle()
    try:
        app.canvas.get_tk_widget().update_idletasks()
    except Exception:
        pass


def _current_view_mode(app) -> str:
    if hasattr(app, "view_mode"):
        return app.view_mode.get()
    return DEFAULT_VIEW_MODE


def _reset_axes(app) -> None:
    app.figure.clf()
    app.ax = app.figure.add_subplot(111)


def update_plot(app):
    try:
        view = _current_view_mode(app)
        entries = get_visible_entries(app)

        _reset_axes(app)
        redraw_background(app)
        redraw_shot_zone_overlay(app)
        _draw_current_view(app, entries, view)
        _apply_default_axes(app)
        _refresh_canvas(app)

    except Exception as e:
        print("❌ update_plot error:", e)


def _is_valid_slider_value(value: float) -> bool:
    return SLIDER_MIN_VALUE < value <= SLIDER_MAX_VALUE


def _apply_slider_entry_value(app, variable, entry, from_slider: bool) -> None:
    if from_slider:
        val = float(variable.get())
        entry.delete(0, tk.END)
        entry.insert(0, f"{val:.2f}")
    else:
        val = float(entry.get())
        if _is_valid_slider_value(val):
            variable.set(val)


def apply_sensitivity(app, from_slider=False):
    try:
        _apply_slider_entry_value(app, app.sensitivity, app.sens_entry, from_slider)
        update_plot(app)
    except Exception:
        print("⛔ Invalid sensitivity input")


def apply_kde(app, from_slider=False):
    try:
        _apply_slider_entry_value(app, app.kde_bandwidth, app.kde_entry, from_slider)
        update_plot(app)
    except Exception:
        print("⛔ Invalid KDE bandwidth input")
