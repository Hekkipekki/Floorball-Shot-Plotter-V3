import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches

from core.entry_helpers import get_result, get_type, get_xy
from gui.constants import (
    PLOT_POINT_EDGE_COLOR,
    PLOT_POINT_EDGE_WIDTH,
    PLOT_SHOT_SIZE,
    PLOT_GOAL_SIZE,
    PLOT_SHOT_ZORDER,
    PLOT_GOAL_ZORDER,
    PLOT_GOAL_COLOR,
    PLOT_FALLBACK_SHOT_COLOR,
    PLOT_FALLBACK_SHOT_LABEL,
    PLOT_SHOT_TYPE_STYLES,
    PLOT_LEGEND_LOC,
    PLOT_LEGEND_BBOX,
    PLOT_LEGEND_FRAME_ON,
    PLOT_LEGEND_FACE_COLOR,
    PLOT_LEGEND_EDGE_COLOR,
    PLOT_LEGEND_FONT_SIZE,
    PLOT_LEGEND_LABEL_SPACING,
    PLOT_LEGEND_HANDLE_LENGTH,
    PLOT_LEGEND_BORDER_PAD,
    PLOT_LEGEND_BORDER_AXES_PAD,
    PLOT_LEGEND_FRAME_ALPHA,
)


def plot_points(app, entries):
    shots = [e for e in entries if get_result(e) == "S"]
    goals = [e for e in entries if get_result(e) == "G"]

    goal_points = [get_xy(e) for e in goals]
    goal_points = [(x, y) for x, y in goal_points if x is not None and y is not None]

    goal_x = [x for x, _ in goal_points]
    goal_y = [y for _, y in goal_points]

    seen_types = set()
    legend_patches = []

    for entry in shots:
        shot_type = (get_type(entry) or "").strip()
        x, y = get_xy(entry)
        if x is None or y is None:
            continue

        color, label = PLOT_SHOT_TYPE_STYLES.get(
            shot_type,
            (PLOT_FALLBACK_SHOT_COLOR, PLOT_FALLBACK_SHOT_LABEL),
        )

        app.ax.scatter(
            x,
            y,
            c=color,
            s=PLOT_SHOT_SIZE,
            edgecolors=PLOT_POINT_EDGE_COLOR,
            linewidths=PLOT_POINT_EDGE_WIDTH,
            zorder=PLOT_SHOT_ZORDER,
        )

        if label not in seen_types:
            seen_types.add(label)
            legend_patches.append(mpatches.Patch(color=color, label=label))

    if goal_points:
        app.ax.scatter(
            goal_x,
            goal_y,
            c=PLOT_GOAL_COLOR,
            s=PLOT_GOAL_SIZE,
            edgecolors=PLOT_POINT_EDGE_COLOR,
            linewidths=PLOT_POINT_EDGE_WIDTH,
            zorder=PLOT_GOAL_ZORDER,
        )
        legend_patches.append(mpatches.Patch(color=PLOT_GOAL_COLOR, label="Goal"))

    if legend_patches:
        app.ax.legend(
            handles=legend_patches,
            loc=PLOT_LEGEND_LOC,
            bbox_to_anchor=PLOT_LEGEND_BBOX,
            frameon=PLOT_LEGEND_FRAME_ON,
            facecolor=PLOT_LEGEND_FACE_COLOR,
            edgecolor=PLOT_LEGEND_EDGE_COLOR,
            fontsize=PLOT_LEGEND_FONT_SIZE,
            labelspacing=PLOT_LEGEND_LABEL_SPACING,
            handlelength=PLOT_LEGEND_HANDLE_LENGTH,
            borderpad=PLOT_LEGEND_BORDER_PAD,
            borderaxespad=PLOT_LEGEND_BORDER_AXES_PAD,
            framealpha=PLOT_LEGEND_FRAME_ALPHA,
        )

    app.ax.set_xlim(app.original_xlim)
    app.ax.set_ylim(app.original_ylim)


def plot_heatmap(app, entries, view_type):
    if view_type == "Goal Heatmap":
        entries = [e for e in entries if get_result(e) == "G"]
    elif view_type == "Save Heatmap":
        entries = [e for e in entries if get_result(e) == "S"]
    elif view_type == "Heatmap":
        entries = [e for e in entries if get_result(e) in ("S", "G")]

    points = [get_xy(e) for e in entries]
    points = [(x, y) for x, y in points if x is not None and y is not None]

    if len(points) < 3:
        print("⚠️ Too few points to compute KDE.")
        return

    x = [x for x, _ in points]
    y = [y for _, y in points]

    nbins = app.resolution_options[app.resolution_preset.get()]
    bandwidth = app.kde_bandwidth.get()
    sensitivity = app.sensitivity.get()
    cmap_name = app.cmap.get()

    print(f"📍 [plot_heatmap] {view_type} entries:")
    for entry in entries:
        result = get_result(entry)
        px, py = get_xy(entry)
        if px is not None and py is not None:
            print(f"   → {result} {px}, {py}")
    print(f"🔍 HEATMAP → nbins={nbins}, bandwidth={bandwidth:.2f}, sensitivity={sensitivity:.2f}")

    values = np.vstack([x, y])
    kernel = gaussian_kde(values, bw_method=bandwidth)

    width = app.original_xlim[1]
    height = app.original_ylim[0]
    xi, yi = np.mgrid[0:width:nbins * 1j, 0:height:nbins * 1j]
    coords = np.vstack([xi.ravel(), yi.ravel()])
    zi = kernel(coords).reshape(xi.shape)

    zi = np.clip(zi, 0, None)
    zi = np.ma.masked_where(zi < max(zi.max() * sensitivity, 1e-8), zi)

    app.ax.imshow(
        zi.T,
        cmap=cmap_name,
        alpha=0.6,
        extent=[*app.original_xlim, *app.original_ylim],
        origin="upper",
        aspect="auto",
        interpolation="none",
    )