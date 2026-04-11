import ttkbootstrap as tb
from tkinter import ttk

from gui.constants import PAD_X, SECTION_PAD_X, SECTION_PAD_Y
from utils.tooltips import BetterToolTip


def setup_stats_filter_controls(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Statistics", bootstyle="primary")
    frame.pack(fill="x", pady=SECTION_PAD_Y, padx=SECTION_PAD_X)

    stats = tb.Frame(frame)
    stats.pack(anchor="center", padx=PAD_X, pady=(PAD_X, 0))
    stats.grid_columnconfigure(0, weight=1)
    stats.grid_columnconfigure(1, weight=1)

    def label_row(row, text, var_attr):
        label = tb.Label(stats, text=text, font=("Segoe UI", 10))
        label.grid(row=row, column=0, sticky="w", padx=(PAD_X, 0), pady=2)

        value = tb.Label(stats, text="0", anchor="w", font=("Segoe UI", 11))
        value.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
        setattr(app, var_attr, value)

    label_row(0, "Shots (Saved):", "shots_val")
    label_row(1, "Goals Conceded:", "goals_val")
    label_row(2, "Total Shots:", "totalshots_val")
    label_row(3, "Save %:", "savepct_val")

    tb.Separator(frame, orient="horizontal").pack(fill="x", pady=(6, 3))

    row = tb.Frame(frame)
    row.pack(anchor="w", padx=PAD_X, pady=(0, PAD_X), fill="x")
    row.grid_columnconfigure(0, weight=1)
    row.grid_columnconfigure(1, weight=1)

    tb.Label(row, text="Filter by Period:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")

    period_options = ["All", "1", "2", "3", "OT"]
    app.stats_period_dropdown = ttk.Combobox(
        row,
        textvariable=app.stats_period,
        values=period_options,
        state="readonly",
        width=9,
        bootstyle="info",
    )
    app.stats_period_dropdown.grid(row=0, column=1, sticky="e")
    app.stats_period_dropdown.bind("<<ComboboxSelected>>", lambda e: app.update_stats_filtered())


def setup_expected_goals_controls(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Expected Goals", bootstyle="primary")
    frame.pack(fill="x", pady=SECTION_PAD_Y, padx=SECTION_PAD_X)

    stats = tb.Frame(frame)
    stats.pack(anchor="center", padx=PAD_X, pady=(PAD_X, PAD_X))
    stats.grid_columnconfigure(0, weight=1)
    stats.grid_columnconfigure(1, weight=1)

    tooltip = "Expected Goals (xG): how many goals should have been conceded based on shot quality."

    label_xg = tb.Label(stats, text="xG Goals:", font=("Segoe UI", 11))
    label_xg.grid(row=0, column=0, sticky="w", padx=(PAD_X, 0), pady=1)

    app.xg_goals_val = tb.Label(stats, text="0.00", anchor="w", font=("Segoe UI", 11))
    app.xg_goals_val.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=1)

    label_goals = tb.Label(stats, text="Goals:", font=("Segoe UI", 11))
    label_goals.grid(row=1, column=0, sticky="w", padx=(PAD_X, 0), pady=1)

    app.actual_goals_val = tb.Label(stats, text="0", anchor="w", font=("Segoe UI", 11))
    app.actual_goals_val.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=1)

    for widget in [frame, label_xg, app.xg_goals_val, label_goals, app.actual_goals_val]:
        BetterToolTip(widget, tooltip)