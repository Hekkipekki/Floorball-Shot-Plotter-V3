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
STATS_VALUE_DEFAULT = "0"
XG_VALUE_DEFAULT = "0.00"


def _configure_two_column_grid(frame: tb.Frame) -> None:
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=1)


def _create_stats_grid(parent: tb.Frame, pady) -> tb.Frame:
    frame = tb.Frame(parent)
    frame.pack(anchor="center", padx=PAD_X, pady=pady)
    _configure_two_column_grid(frame)
    return frame


def _add_stat_row(
    app,
    parent: tb.Frame,
    row: int,
    text: str,
    var_attr: str,
    value_text: str = STATS_VALUE_DEFAULT,
) -> tuple[tb.Label, tb.Label]:
    label = tb.Label(parent, text=text, font=("Segoe UI", 10))
    label.grid(row=row, column=0, sticky="w", padx=(PAD_X, 0), pady=2)

    value = tb.Label(parent, text=value_text, anchor="w", font=("Segoe UI", 11))
    value.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
    setattr(app, var_attr, value)
    return label, value


def setup_stats_filter_controls(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Statistics", bootstyle="primary")
    frame.pack(fill="x", pady=SECTION_PAD_Y, padx=SECTION_PAD_X)

    stats = _create_stats_grid(frame, pady=(PAD_X, 0))

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

    stats = _create_stats_grid(frame, pady=(PAD_X, PAD_X))

    label_xg, _ = _add_stat_row(
        app,
        stats,
        row=0,
        text="xG Goals:",
        var_attr="xg_goals_val",
        value_text=XG_VALUE_DEFAULT,
    )
    label_goals, _ = _add_stat_row(
        app,
        stats,
        row=1,
        text="Goals:",
        var_attr="actual_goals_val",
        value_text=STATS_VALUE_DEFAULT,
    )

    for widget in [frame, label_xg, app.xg_goals_val, label_goals, app.actual_goals_val]:
        BetterToolTip(widget, EXPECTED_GOALS_TOOLTIP)
