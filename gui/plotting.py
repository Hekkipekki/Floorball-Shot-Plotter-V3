import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.patches as mpatches

def plot_points(app, entries):
    shots = [e for e in entries if e[1] == "S"]
    goals = [e for e in entries if e[1] == "G"]

    shot_x = [e[9] for e in shots]  # X
    shot_y = [e[10] for e in shots]  # Y
    shot_types = [e[4] for e in shots]  # Shot Type

    goal_x = [e[9] for e in goals]
    goal_y = [e[10] for e in goals]

    # 🎨 Färgkarta för olika skotttyper
    color_map = {
        "One-timer": ("blue", "One-timer"),
        "Controlled shot": ("orange", "Controlled shot"),
        "Own Goal": ("black", "Own Goal"),
        "Deke": ("purple", "Deke"),
        "Deflection": ("green", "Deflection")
    }

    seen_types = set()
    legend_patches = []

    # 🔵 Rita alla skott
    for entry in shots:
        shot_type = entry[4].strip()
        x, y = entry[9], entry[10]  # X, Y
        color_label = color_map.get(shot_type)
        if color_label:
            color, label = color_label
        else:
            color, label = "gray", "Other"

        app.ax.scatter(x, y, c=color, s=60, edgecolors='black', linewidths=0.5, zorder=5)

        if label not in seen_types:
            seen_types.add(label)
            legend_patches.append(mpatches.Patch(color=color, label=label))

    # 🔴 Rita mål (separat)
    if goals:
        app.ax.scatter(goal_x, goal_y, c='red', s=70, edgecolors='black', linewidths=0.5, zorder=6)
        legend_patches.append(mpatches.Patch(color='red', label='Goal'))

    # 📌 Dynamisk legend nere till höger
    if legend_patches:
        app.ax.legend(
            handles=legend_patches,
            loc='lower right',
            bbox_to_anchor=(1.055, -0.055),
            frameon=True,
            facecolor='white',
            edgecolor='black',
            fontsize=10,
            labelspacing=0.4,
            handlelength=1.8,
            borderpad=0.7,
            borderaxespad=0.4,
            framealpha=1.0
        )

    app.ax.set_xlim(app.original_xlim)
    app.ax.set_ylim(app.original_ylim)


def plot_heatmap(app, entries, view_type):
    if view_type == "Goal Heatmap":
        entries = [e for e in entries if e[1] == "G"]
    elif view_type == "Save Heatmap":
        entries = [e for e in entries if e[1] == "S"]
    elif view_type == "Heatmap":
        entries = [e for e in entries if e[1] in ("S", "G")]

    x = [e[9] for e in entries]  # X
    y = [e[10] for e in entries]  # Y

    if len(entries) < 3:
        print("⚠️ Too few points to compute KDE.")
        return

    nbins = app.resolution_options[app.resolution_preset.get()]
    bandwidth = app.kde_bandwidth.get()
    sensitivity = app.sensitivity.get()
    cmap_name = app.cmap.get()

    print(f"📍 [plot_heatmap] {view_type} entries:")
    for e in entries:
        print(f"   → {e[1]} {e[9]}, {e[10]}")
    print(f"🔍 HEATMAP → nbins={nbins}, bandwidth={bandwidth:.2f}, sensitivity={sensitivity:.2f}")

    values = np.vstack([x, y])
    kernel = gaussian_kde(values, bw_method=bandwidth)

    width = app.original_xlim[1]
    height = app.original_ylim[0]
    xi, yi = np.mgrid[0:width:nbins*1j, 0:height:nbins*1j]
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
        interpolation="none"
    )
