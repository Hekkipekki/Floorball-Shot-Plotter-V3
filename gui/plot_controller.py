# gui/plot_controller.py
"""
Plot controller for Floorball Shot Plotter.

Fixes / improvements vs your current version:
- Uses ONE source of truth for what is displayed: app.logic.get_filtered_entries()
  (so plot / hover / highlight / remove-nearest all match what the user sees)
- Removes duplicate / contradictory checks in hover handler
- Keeps background + axis limits consistent
- Adds click-to-store last rink click (for Remove Nearest)
- Adds remove_nearest_point(app) that deletes from MASTER match_logs (not only filtered view)
- Safer handling of missing indices / legacy entries
"""

from __future__ import annotations

import os
import math
import numpy as np
import tkinter as tk
from PIL import Image
from matplotlib.patches import FancyArrowPatch, Patch

from gui.plotting import plot_points, plot_heatmap
from utils.helpers import get_resource_path


# -----------------------------
# Background image
# -----------------------------
def load_image(app):
    """
    Loads background image into app.img and sets app.img_extent, app.img_size,
    and app.original_xlim/ylim to match the image size.

    Expected: app.selected_background is a tk.StringVar containing filename.
    """
    app.img = None
    path = get_resource_path("Resources", app.selected_background.get())

    try:
        if os.path.exists(path):
            original = Image.open(path).convert("RGB")
            w, h = original.size

            # Keep scale 1.0 for now, but leave it as a variable if you want.
            scale = 1.0
            new_size = (int(w * scale), int(h * scale))
            original = original.resize(new_size, Image.Resampling.LANCZOS)

            app.img = np.array(original)
            app.img_size = new_size
            app.img_extent = [0, new_size[0], new_size[1], 0]

            # Coordinate system matches your rink coords: X 0..width, Y 0..height (top origin)
            app.original_xlim = (0, new_size[0])
            app.original_ylim = (new_size[1], 0)
        else:
            _set_default_canvas_dimensions(app)
    except Exception:
        _set_default_canvas_dimensions(app)


def _set_default_canvas_dimensions(app):
    app.img_size = (1500, 1000)
    app.img_extent = [0, 1500, 1000, 0]
    app.original_xlim = (0, 1500)
    app.original_ylim = (1000, 0)


def refresh_image(app):
    load_image(app)
    update_plot(app)


# -----------------------------
# Entries helpers
# -----------------------------
def _get_visible_entries(app):
    """
    Always return what the user sees right now.
    Prefer CoreLogic's filtered view if available.
    """
    try:
        if hasattr(app, "logic") and hasattr(app.logic, "get_filtered_entries"):
            return list(app.logic.get_filtered_entries())
    except Exception:
        pass

    # Fallback: raw
    return list(getattr(app, "log_entries", []))


def _safe_get_xy(entry):
    """
    Your structure: X index 9, Y index 10.
    Return (x,y) or (None,None) if invalid.
    """
    try:
        x = float(entry[9])
        y = float(entry[10])
        return x, y
    except Exception:
        return None, None


def _find_nearest_index(entries, target_x, target_y):
    best_i = None
    best_d2 = float("inf")

    for i, e in enumerate(entries):
        x, y = _safe_get_xy(e)
        if x is None:
            continue
        d2 = (x - target_x) ** 2 + (y - target_y) ** 2
        if d2 < best_d2:
            best_d2 = d2
            best_i = i

    return best_i


# -----------------------------
# Plot updating
# -----------------------------
def update_plot(app):
    """
    Rebuild the plot from scratch based on current view mode and filters.
    """
    try:
        view = app.view_mode.get() if hasattr(app, "view_mode") else "Plot"
        entries = _get_visible_entries(app)

        # Clear figure/axes
        app.figure.clf()
        app.ax = app.figure.add_subplot(111)

        # Draw background image if available
        if getattr(app, "img", None) is not None:
            extent = getattr(app, "img_extent", [0, 1500, 1000, 0])
            app.ax.imshow(app.img, extent=extent, origin="upper", aspect="auto")

        # Normalize view naming (your app uses "Plot", "Heatmap", etc.)
        if view in ("Heatmap", "Goal Heatmap", "Save Heatmap"):
            plot_heatmap(app, entries, view)
            app.ax.axis("off")
        elif view == "Plot":
            plot_points(app, entries)
            app.ax.axis("off")
        else:
            # Unknown view -> fallback to plot points
            plot_points(app, entries)
            app.ax.axis("off")

        # Apply consistent axis limits
        app.ax.set_xlim(getattr(app, "original_xlim", (0, 1500)))
        app.ax.set_ylim(getattr(app, "original_ylim", (1000, 0)))
        app.ax.axis("off")

        # Draw
        app.canvas.draw_idle()
        try:
            app.canvas.get_tk_widget().update_idletasks()
        except Exception:
            pass

    except Exception as e:
        print("❌ update_plot error:", e)


# -----------------------------
# Slider handlers
# -----------------------------
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


# -----------------------------
# Highlight (used by shotlog hover/click)
# -----------------------------
def draw_pass_arrow(ax, pass_x, pass_y, shot_x, shot_y, offset=15):
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
        color="red",
        linewidth=2,
        mutation_scale=15,
        zorder=8,
    )
    ax.add_patch(arrow)
    return arrow


def highlight_point(app, index):
    """
    Highlight an entry from the CURRENT visible list (filtered).
    This fixes mismatch issues where hovering a filtered row highlighted wrong point.
    """
    view = app.view_mode.get() if hasattr(app, "view_mode") else "Plot"
    if view in ("Heatmap", "Goal Heatmap", "Save Heatmap"):
        return

    entries = _get_visible_entries(app)
    if not (0 <= index < len(entries)):
        return

    entry = entries[index]
    x, y = _safe_get_xy(entry)
    if x is None:
        return

    # Rebuild axes (clear)
    app.ax.cla()

    # Background again
    if getattr(app, "img", None) is not None:
        app.ax.imshow(app.img, extent=getattr(app, "img_extent", [0, 1500, 1000, 0]), origin="upper", aspect="auto")

    # Track artists so we can remove (optional)
    app.highlighted = []

    passer = entry[5] if len(entry) > 5 else ""
    shooter = entry[6] if len(entry) > 6 else ""

    # Shot point
    if len(entry) > 1 and entry[1] == "G":
        shot = app.ax.scatter(x, y, s=70, c="red", edgecolors="black", linewidths=1, zorder=10)
    else:
        shot = app.ax.scatter(x, y, s=120, edgecolors="yellow", facecolors="none", linewidths=2, zorder=10)
    app.highlighted.append(shot)

    # Shooter stick label
    if shooter in ("Left", "Right"):
        dx = 22 if shooter == "Left" else -22
        label = app.ax.text(
            x + dx,
            y,
            "L" if shooter == "Left" else "R",
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center",
            bbox=dict(facecolor="white", edgecolor="black", boxstyle="circle"),
            zorder=11,
        )
        app.highlighted.append(label)

    # Pass point & arrow if present
    # Your structure: Pass X index 11, Pass Y index 12
    pass_x = entry[11] if len(entry) > 11 else None
    pass_y = entry[12] if len(entry) > 12 else None

    if pass_x is not None and pass_y is not None:
        try:
            px, py = float(pass_x), float(pass_y)
            assist = app.ax.scatter(px, py, s=90, c="deepskyblue", marker="X", edgecolors="black", linewidths=1.5, zorder=9)
            app.highlighted.append(assist)

            if passer in ("Left", "Right"):
                dx_pass = 22 if passer == "Left" else -22
                label_pass = app.ax.text(
                    px + dx_pass,
                    py,
                    "L" if passer == "Left" else "R",
                    fontsize=10,
                    fontweight="bold",
                    ha="center",
                    va="center",
                    bbox=dict(facecolor="white", edgecolor="black", boxstyle="circle"),
                    zorder=10,
                )
                app.highlighted.append(label_pass)

            arrow = draw_pass_arrow(app.ax, px, py, x, y, offset=15)
            app.highlighted.append(arrow)
        except Exception:
            pass

    # Simple legend (optional)
    color_map = {
        "shot": ("blue", "Shot"),
        "rebound": ("orange", "Rebound"),
        "penalty": ("pink", "Penalty"),
        "2v1": ("green", "2v1"),
        "breakaway": ("purple", "Breakaway"),
    }

    legend_patches = []
    if len(entry) > 1 and entry[1] == "G":
        legend_patches.append(Patch(color="red", label="Goal"))
    else:
        shot_type = entry[4] if len(entry) > 4 else ""
        color, label = color_map.get(shot_type, ("gray", "Other"))
        legend_patches.append(Patch(color=color, label=label))

    if legend_patches:
        app.ax.legend(
            handles=legend_patches,
            loc="lower right",
            bbox_to_anchor=(1.05, -0.02),
            frameon=True,
            facecolor="white",
            edgecolor="black",
            fontsize=10,
            labelspacing=0.4,
            handlelength=1.8,
            borderpad=0.7,
            borderaxespad=0.4,
            framealpha=1.0,
        )

    # Limits/off
    app.ax.set_xlim(getattr(app, "original_xlim", (0, 1500)))
    app.ax.set_ylim(getattr(app, "original_ylim", (1000, 0)))
    app.ax.axis("off")

    app.is_hover_preview = True
    app.canvas.draw_idle()


def clear_highlight(app):
    # If we are showing a hover preview, return to normal plot
    if getattr(app, "is_hover_preview", False):
        update_plot(app)
        app.is_hover_preview = False


# -----------------------------
# Hover + click connect
# -----------------------------
def connect_hover_events(app):
    """
    - Hover highlights nearest point (visible entries only)
    - Click stores last rink click (so Remove Nearest can work reliably)
    """
    # Avoid double-connecting if you call this more than once
    if getattr(app, "_hover_connected", False):
        return
    app._hover_connected = True

    def on_motion(event):
        # Only in plot mode
        if app.view_mode.get() != "Plot":
            return
        if not event.inaxes or event.x is None or event.y is None:
            return

        entries = _get_visible_entries(app)
        if not entries:
            return

        threshold_px = 15
        found_index = None

        # Compare in DISPLAY coords for consistent threshold
        for idx, entry in enumerate(entries):
            x, y = _safe_get_xy(entry)
            if x is None:
                continue
            disp_x, disp_y = app.ax.transData.transform((x, y))
            dist = np.hypot(disp_x - event.x, disp_y - event.y)
            if dist < threshold_px:
                found_index = idx
                break

        if found_index is not None:
            app._hover_index = found_index
            highlight_point(app, found_index)
        else:
            app._hover_index = None
            clear_highlight(app)

    def on_click(event):
        # store last click in data coords
        if not event.inaxes or event.xdata is None or event.ydata is None:
            return
        try:
            app._last_rink_click = (float(event.xdata), float(event.ydata))
        except Exception:
            app._last_rink_click = None

        # make sure keyboard focus returns so Space works
        try:
            app.root.focus_set()
        except Exception:
            pass

    app.canvas.mpl_connect("motion_notify_event", on_motion)
    app.canvas.mpl_connect("button_press_event", on_click)


# -----------------------------
# Remove nearest (Space)
# -----------------------------
def remove_nearest_point(app, event=None):
    """
    Remove nearest visible entry, but delete from MASTER match_logs.
    Priority:
      1) hovered row (app._hover_index)
      2) last click on rink (app._last_rink_click)
      3) last visible entry
    """
    if getattr(app, "popup_open", False):
        return

    visible = _get_visible_entries(app)
    if not visible:
        return

    entry_to_remove = None

    hover_idx = getattr(app, "_hover_index", None)
    if hover_idx is not None and 0 <= hover_idx < len(visible):
        entry_to_remove = visible[hover_idx]
    else:
        last_click = getattr(app, "_last_rink_click", None)
        if last_click:
            tx, ty = last_click
            ni = _find_nearest_index(visible, tx, ty)
            if ni is not None:
                entry_to_remove = visible[ni]

    if entry_to_remove is None:
        entry_to_remove = visible[-1]

    match_name = app.current_match.get()

    def _remove_from_list(lst):
        # Exact tuple remove first
        try:
            lst.remove(entry_to_remove)
            return True
        except ValueError:
            pass

        # Fallback: match by number + SG + XY (safer if tuple objects differ)
        try:
            tnum = entry_to_remove[0]
            tsg = entry_to_remove[1]
            tx, ty = _safe_get_xy(entry_to_remove)
            for i, e in enumerate(lst):
                if not e:
                    continue
                ex, ey = _safe_get_xy(e)
                if e[0] == tnum and e[1] == tsg and ex == tx and ey == ty:
                    del lst[i]
                    return True
        except Exception:
            pass

        return False

    removed = False

    # Remove from master
    if match_name in ("All", "Season"):
        for name, lst in app.match_logs.items():
            if name in ("All", "Season"):
                continue
            if _remove_from_list(lst):
                removed = True
                break
    else:
        lst = app.match_logs.get(match_name, [])
        removed = _remove_from_list(lst)

    if not removed:
        return

    # Refresh everything
    app.update_log_view_and_stats()