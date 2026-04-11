import tkinter as tk
import ttkbootstrap as tb
from tkinter import ttk

from gui.constants import (
    ENTRY_SMALL_WIDTH,
    PAD_X,
    PRESET_DESCRIPTION_WRAP,
    SECTION_PAD_X,
)


def setup_heatmap_settings_group(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Heatmap Settings", bootstyle="primary")
    frame.pack(fill="x", pady=(3, 0), padx=SECTION_PAD_X)

    tb.Label(frame, text="Select heatmap color:", font=("Segoe UI", 10)).pack(
        padx=PAD_X, pady=(2, 1), anchor="w"
    )
    app.colormap_combobox = ttk.Combobox(
        frame,
        values=["inferno", "plasma", "magma", "hot", "jet"],
        textvariable=app.cmap,
        state="readonly",
        bootstyle="primary",
    )
    app.colormap_combobox.pack(fill="x", padx=PAD_X, pady=(0, 2))
    app.colormap_combobox.bind("<<ComboboxSelected>>", lambda e: app.update_plot())

    tb.Label(frame, text="Heatmap Quality:", font=("Segoe UI", 10)).pack(
        padx=PAD_X, pady=(1, 1), anchor="w"
    )
    app.resolution_combobox = ttk.Combobox(
        frame,
        values=list(app.resolution_options.keys()),
        textvariable=app.resolution_preset,
        state="readonly",
        bootstyle="primary",
    )
    app.resolution_combobox.pack(fill="x", padx=PAD_X, pady=(0, 2))
    app.resolution_combobox.bind("<<ComboboxSelected>>", lambda e: app.update_plot())

    tb.Label(frame, text="Preset:", font=("Segoe UI", 10)).pack(
        padx=PAD_X, pady=(1, 1), anchor="w"
    )
    app.heatmap_preset = tk.StringVar(value="Match Analysis")
    app.heatmap_preset_dropdown = ttk.Combobox(
        frame,
        values=[
            "Match Analysis",
            "Multi-Match",
            "Season Review",
            "Season Review (Goal only)",
        ],
        textvariable=app.heatmap_preset,
        state="readonly",
        bootstyle="primary",
    )
    app.heatmap_preset_dropdown.pack(fill="x", padx=PAD_X, pady=(0, 2))
    app.heatmap_preset_dropdown.bind("<<ComboboxSelected>>", lambda e: app.on_preset_changed())

    app.preset_description = tb.Label(
        frame,
        text="",
        font=("Segoe UI", 8, "italic"),
        wraplength=PRESET_DESCRIPTION_WRAP,
        justify="left",
    )
    app.preset_description.pack(padx=PAD_X, pady=(0, PAD_X), anchor="w")

    tb.Label(frame, text="Sensitivity:", font=("Segoe UI", 10)).pack(
        padx=PAD_X, pady=(1, 1), anchor="w"
    )
    app.sens_slider = tb.Scale(
        frame,
        from_=0.01,
        to=1.0,
        orient="horizontal",
        variable=app.sensitivity,
        length=110,
        command=lambda val: app.apply_sensitivity(from_slider=True),
    )
    app.sens_slider.pack(fill="x", padx=PAD_X)

    app.sens_entry = tb.Entry(frame, width=ENTRY_SMALL_WIDTH)
    app.sens_entry.insert(0, f"{app.sensitivity.get():.2f}")
    app.sens_entry.pack(padx=PAD_X, pady=(0, 2), anchor="e")
    app.sens_entry.bind("<Return>", lambda e: app.apply_sensitivity(from_slider=False))

    tb.Label(frame, text="KDE Bandwidth:", font=("Segoe UI", 10)).pack(
        padx=PAD_X, pady=(1, 1), anchor="w"
    )
    app.kde_slider = tb.Scale(
        frame,
        from_=0.01,
        to=1.0,
        orient="horizontal",
        variable=app.kde_bandwidth,
        length=110,
        command=lambda val: app.apply_kde(from_slider=True),
    )
    app.kde_slider.pack(fill="x", padx=PAD_X)

    app.kde_entry = tb.Entry(frame, width=ENTRY_SMALL_WIDTH)
    app.kde_entry.insert(0, f"{app.kde_bandwidth.get():.2f}")
    app.kde_entry.pack(padx=PAD_X, pady=(0, 2), anchor="e")
    app.kde_entry.bind("<Return>", lambda e: app.apply_kde(from_slider=False))