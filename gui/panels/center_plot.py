from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui.constants import (
    FIGURE_HEIGHT,
    FIGURE_SUBPLOT_BOTTOM,
    FIGURE_SUBPLOT_LEFT,
    FIGURE_SUBPLOT_RIGHT,
    FIGURE_SUBPLOT_TOP,
    FIGURE_WIDTH,
)
from gui.events import onclick
from gui.point_removal import remove_nearest_point
from utils.tooltips import BetterToolTip

HOTKEYS_TOOLTIP = (
    "🎯 Hotkeys:\n\n"
    "👡 Left Click  = Add Shot\n"
    "👡 Right Click = Add Goal\n"
    "⎵ Space       = Remove Nearest Dot\n"
    "👡 Double Click (Shot Log) = Delete Entry\n"
    "👡 Right Click (Shot Log) = Link / Play Video"
)
HOTKEYS_LABEL_TEXT = "ⓘ Hotkeys Info"
HOTKEYS_LABEL_BG = "lightyellow"
HOTKEYS_LABEL_FONT = ("Arial", 9, "bold")
HOTKEYS_LABEL_X = 5
HOTKEYS_LABEL_Y = 5
SELECTOR_MARKER_SIZE = 15
SELECTOR_MARKER_ALPHA = 0.5


def _create_plot_figure() -> Figure:
    figure = Figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
    figure.subplots_adjust(
        left=FIGURE_SUBPLOT_LEFT,
        right=FIGURE_SUBPLOT_RIGHT,
        top=FIGURE_SUBPLOT_TOP,
        bottom=FIGURE_SUBPLOT_BOTTOM,
    )
    return figure


def _store_plot_widgets(app, frame: tb.Frame, figure: Figure, canvas: FigureCanvasTkAgg) -> None:
    app.figure = figure
    app.ax = figure.axes[0]
    app.canvas = canvas

    # Keep compatibility with older code that expects canvas_frame to exist
    app.canvas_frame = frame

    # Optional compatibility with older plot code
    app.selector_dot, = app.ax.plot([], [], "o", markersize=SELECTOR_MARKER_SIZE, alpha=SELECTOR_MARKER_ALPHA)
    app.highlight_artist = None


def _bind_plot_events(app, canvas_widget) -> None:
    canvas_widget.focus_set()
    canvas_widget.bind("<space>", lambda e: remove_nearest_point(app, e))
    app.canvas.mpl_connect("button_press_event", lambda e: onclick(app, e))


def _create_hotkeys_label(parent) -> tk.Label:
    label = tk.Label(
        parent,
        text=HOTKEYS_LABEL_TEXT,
        bg=HOTKEYS_LABEL_BG,
        font=HOTKEYS_LABEL_FONT,
        relief="ridge",
        borderwidth=1,
    )
    label.place(x=HOTKEYS_LABEL_X, y=HOTKEYS_LABEL_Y)
    BetterToolTip(label, HOTKEYS_TOOLTIP)
    return label


def create_center_plot(parent, app):
    frame = tb.Frame(parent)
    frame.pack(side="left", fill="both", expand=True)

    figure = _create_plot_figure()
    figure.add_subplot(111)

    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill="both", expand=True)

    _store_plot_widgets(app, frame, figure, canvas)
    _bind_plot_events(app, canvas_widget)

    app.instructions_label = _create_hotkeys_label(canvas_widget)

    return frame
