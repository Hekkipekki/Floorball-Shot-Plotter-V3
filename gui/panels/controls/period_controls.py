import ttkbootstrap as tb
from tkinter import ttk

from gui.constants import PAD_X, SECTION_PAD_X, SECTION_PAD_Y
from utils.tooltips import BetterToolTip

PERIOD_OPTIONS = ["1", "2", "3", "OT", "All"]
PERIOD_TOOLTIPS = {
    "1": "Select to log events to Period 1.",
    "2": "Select to log events to Period 2.",
    "3": "Select to log events to Period 3.",
    "OT": "Select to log events to Overtime.",
    "All": "Show events from all periods.",
}
VIEW_MODE_OPTIONS = ["Plot", "Heatmap", "Goal Heatmap", "Save Heatmap"]
VIEW_MODE_TOOLTIP = (
    "Change the visualization mode:\n"
    "- Plot = regular shot plot\n"
    "- Heatmaps = density views of shots or goals"
)
DEFAULT_VIEW_MODE = "Plot"


def _period_button_width(period: str) -> int:
    if period == "All":
        return 4
    if period == "OT":
        return 3
    return 2


def _create_control_group(parent: tb.Frame, title: str) -> tb.Labelframe:
    frame = tb.Labelframe(parent, text=title, bootstyle="primary")
    frame.pack(fill="x", expand=False, pady=SECTION_PAD_Y, padx=SECTION_PAD_X)
    return frame


def _create_period_button(app, parent: tb.Frame, period: str) -> tb.Button:
    button = tb.Button(
        parent,
        text=period,
        command=lambda p=period: app.set_period_filter(p),
        width=_period_button_width(period),
        bootstyle="primary",
    )
    button.pack(side="left", padx=3, pady=(2, 4))
    BetterToolTip(button, PERIOD_TOOLTIPS[period])
    return button


def setup_period_controls(app, parent: tb.Frame) -> None:
    frame = _create_control_group(parent, "Period")
    BetterToolTip(frame, "Select if you want to log shots/goals to a specific period.")

    button_frame = tb.Frame(frame)
    button_frame.pack(fill="x", padx=PAD_X, pady=(3, 3))

    app.period_buttons = {}

    for period in PERIOD_OPTIONS:
        app.period_buttons[period] = _create_period_button(app, button_frame, period)

    app.period_selected.trace("w", lambda *args: app.update_period_button_styles())


def setup_view_mode_controls(app, parent: tb.Frame) -> None:
    frame = _create_control_group(parent, "View Mode")
    app.view_mode.set(DEFAULT_VIEW_MODE)

    def on_select(event=None):
        selected = app.view_mode_dropdown.get()
        app.view_mode.set(selected)
        app.update_plot()

    app.view_mode_dropdown = ttk.Combobox(
        frame,
        values=VIEW_MODE_OPTIONS,
        textvariable=app.view_mode,
        state="readonly",
        bootstyle="info",
    )
    app.view_mode_dropdown.pack(fill="x", padx=PAD_X)
    app.view_mode_dropdown.bind("<<ComboboxSelected>>", on_select)

    BetterToolTip(app.view_mode_dropdown, VIEW_MODE_TOOLTIP)
