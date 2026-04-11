from __future__ import annotations

import tkinter as tk

from core.entry_helpers import get_xy
from gui.constants import PLOT_DEFAULT_XLIM, PLOT_DEFAULT_YLIM
from gui.plotting import plot_points, plot_heatmap


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


def redraw_background(app):
    if getattr(app, "img", None) is not None:
        app.ax.imshow(
            app.img,
            extent=getattr(app, "img_extent", [*PLOT_DEFAULT_XLIM, PLOT_DEFAULT_YLIM[0], PLOT_DEFAULT_YLIM[1]]),
            origin="upper",
            aspect="auto",
        )


def update_plot(app):
    try:
        view = app.view_mode.get() if hasattr(app, "view_mode") else "Plot"
        entries = get_visible_entries(app)

        app.figure.clf()
        app.ax = app.figure.add_subplot(111)

        redraw_background(app)

        if view in ("Heatmap", "Goal Heatmap", "Save Heatmap"):
            plot_heatmap(app, entries, view)
            app.ax.axis("off")
        elif view == "Plot":
            plot_points(app, entries)
            app.ax.axis("off")
        else:
            plot_points(app, entries)
            app.ax.axis("off")

        app.ax.set_xlim(getattr(app, "original_xlim", PLOT_DEFAULT_XLIM))
        app.ax.set_ylim(getattr(app, "original_ylim", PLOT_DEFAULT_YLIM))
        app.ax.axis("off")

        app.canvas.draw_idle()
        try:
            app.canvas.get_tk_widget().update_idletasks()
        except Exception:
            pass

    except Exception as e:
        print("❌ update_plot error:", e)


def apply_sensitivity(app, from_slider=False):
    try:
        if from_slider:
            val = float(app.sensitivity.get())
            app.sens_entry.delete(0, tk.END)
            app.sens_entry.insert(0, f"{val:.2f}")
        else:
            val = float(app.sens_entry.get())
            if 0 < val <= 1.0:
                app.sensitivity.set(val)
        update_plot(app)
    except Exception:
        print("⛔ Invalid sensitivity input")


def apply_kde(app, from_slider=False):
    try:
        if from_slider:
            val = float(app.kde_bandwidth.get())
            app.kde_entry.delete(0, tk.END)
            app.kde_entry.insert(0, f"{val:.2f}")
        else:
            val = float(app.kde_entry.get())
            if 0 < val <= 1.0:
                app.kde_bandwidth.set(val)
        update_plot(app)
    except Exception:
        print("⛔ Invalid KDE bandwidth input")