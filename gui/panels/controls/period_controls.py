import ttkbootstrap as tb
from tkinter import ttk

from gui.constants import PAD_X, SECTION_PAD_X, SECTION_PAD_Y
from utils.tooltips import BetterToolTip


def setup_period_controls(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Period", bootstyle="primary")
    frame.pack(fill="x", expand=False, pady=SECTION_PAD_Y, padx=SECTION_PAD_X)
    BetterToolTip(frame, "Select if you want to log shots/goals to a specific period.")

    button_frame = tb.Frame(frame)
    button_frame.pack(fill="x", padx=PAD_X, pady=(3, 3))

    period_buttons = ["1", "2", "3", "OT", "All"]
    tooltip_texts = {
        "1": "Select to log events to Period 1.",
        "2": "Select to log events to Period 2.",
        "3": "Select to log events to Period 3.",
        "OT": "Select to log events to Overtime.",
        "All": "Show events from all periods.",
    }
    app.period_buttons = {}

    for period in period_buttons:
        btn_width = 4 if period == "All" else 3 if period == "OT" else 2
        button = tb.Button(
            button_frame,
            text=period,
            command=lambda p=period: app.set_period_filter(p),
            width=btn_width,
            bootstyle="primary",
        )
        button.pack(side="left", padx=3, pady=(2, 4))
        BetterToolTip(button, tooltip_texts[period])
        app.period_buttons[period] = button

    app.period_selected.trace("w", lambda *args: app.update_period_button_styles())


def setup_view_mode_controls(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="View Mode", bootstyle="primary")
    frame.pack(fill="x", pady=SECTION_PAD_Y, padx=SECTION_PAD_X)

    view_options = ["Plot", "Heatmap", "Goal Heatmap", "Save Heatmap"]
    app.view_mode.set("Plot")

    def on_select(event=None):
        selected = app.view_mode_dropdown.get()
        app.view_mode.set(selected)
        app.update_plot()

    app.view_mode_dropdown = ttk.Combobox(
        frame,
        values=view_options,
        textvariable=app.view_mode,
        state="readonly",
        bootstyle="info",
    )
    app.view_mode_dropdown.pack(fill="x", padx=PAD_X)
    app.view_mode_dropdown.bind("<<ComboboxSelected>>", on_select)

    BetterToolTip(
        app.view_mode_dropdown,
        "Change the visualization mode:\n"
        "- Plot = regular shot plot\n"
        "- Heatmaps = density views of shots or goals",
    )