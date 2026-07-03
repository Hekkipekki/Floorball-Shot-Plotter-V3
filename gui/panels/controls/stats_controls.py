import ttkbootstrap as tb
from tkinter import ttk

from gui.constants import PAD_X, SECTION_PAD_X, SECTION_PAD_Y
from utils.tooltips import BetterToolTip

STAT_ROWS = [
    ("Shots (Saved):", "shots_val"),
    ("Goals Conceded:", "goals_val"),
    ("Total Shots:", "totalshots_val"),
    ("Save %:", "savepct_val"),
]
PERIOD_OPTIONS = ["All", "1", "2", "3", "OT"]
EXPECTED_GOALS_TOOLTIP = (
    "Expected Goals (xG): how many goals should have been conceded based on shot quality."
)


def _configure_two_column_grid(frame: tb.Frame) -> None:
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)


def _add_stat_row(app, parent: tb.Frame, row: int, text: str, var_attr: str) -> None:
    label = tb.Label(parent, text=text, font=("Segoe UI", 10))
    label.grid(row=row, column=0, sticky="w", padx=(PAD_X, 0), pady=2)

    value = tb.Label(parent, text="0", anchor="w", font=("Segoe UI", 11))
    value.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
    setattr(app, var_attr, value)


def setup_stats_filter_controls(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Statistics", bootstyle="primary")
    frame.pack(fill="x", pady=SECTION_PAD_Y, padx=SECTION_PAD_X)

    stats = tb.Frame(frame)
    stats.pack(anchor="center", padx=PAD_X, pady=(PAD_X, 0))
    _configure_two_column_grid(stats)

    for row, (label, var_attr) in enumerate(STAT_ROWS):
        _add_stat_row(app, stats, row, label, var_attr)

    tb.Separator(frame, orient="horizontal").pack(fill="x", pady=(6, 3))

    row = tb.Frame(frame)
    row.pack(anchor="w", padx=PAD_X, pady=(0, PAD_X), fill="x")
    _configure_two_column_grid(row)

    tb.Label(row, text="Filter by Period:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")

    app.stats_period_dropdown = ttk.Combobox(
        row,
        textvariable=app.stats_period,
        values=PERIOD_OPTIONS,
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
    _configure_two_column_grid(stats)

    label_xg = tb.Label(stats, text="xG Goals:", font=("Segoe UI", 11))
    label_xg.grid(row=0, column=0, sticky="w", padx=(PAD_X, 0), pady=1)

    app.xg_goals_val = tb.Label(stats, text="0.00", anchor="w", font=("Segoe UI", 11))
    app.xg_goals_val.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=1)

    label_goals = tb.Label(stats, text="Goals:", font=("Segoe UI", 11))
    label_goals.grid(row=1, column=0, sticky="w", padx=(PAD_X, 0), pady=1)

    app.actual_goals_val = tb.Label(stats, text="0", anchor="w", font=("Segoe UI", 11))
    app.actual_goals_val.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=1)

    for widget in [frame, label_xg, app.xg_goals_val, label_goals, app.actual_goals_val]:
        BetterToolTip(widget, EXPECTED_GOALS_TOOLTIP)
