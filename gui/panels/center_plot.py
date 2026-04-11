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
from gui.events import onclick, on_space_key_pressed
from utils.tooltips import BetterToolTip


def create_center_plot(parent, app):
    frame = tb.Frame(parent)
    frame.pack(side="left", fill="both", expand=True)

    figure = Figure(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
    figure.subplots_adjust(
        left=FIGURE_SUBPLOT_LEFT,
        right=FIGURE_SUBPLOT_RIGHT,
        top=FIGURE_SUBPLOT_TOP,
        bottom=FIGURE_SUBPLOT_BOTTOM,
    )

    ax = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, master=frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill="both", expand=True)

    app.figure = figure
    app.ax = ax
    app.canvas = canvas

    # Keep compatibility with older code that expects canvas_frame to exist
    app.canvas_frame = frame

    # Optional compatibility with older plot code
    app.selector_dot, = app.ax.plot([], [], "o", markersize=15, alpha=0.5)
    app.highlight_artist = None

    # Focus / key binding
    canvas_widget.focus_set()
    canvas_widget.bind("<space>", lambda e: on_space_key_pressed(app, e))

    # Click binding for adding shots / goals
    app.canvas.mpl_connect("button_press_event", lambda e: onclick(app, e))

    # Small info label, same idea as before
    app.instructions_label = tk.Label(
        canvas_widget,
        text="ⓘ Hotkeys Info",
        bg="lightyellow",
        font=("Arial", 9, "bold"),
        relief="ridge",
        borderwidth=1,
    )
    app.instructions_label.place(x=5, y=5)

    BetterToolTip(
        app.instructions_label,
        "🎯 Hotkeys:\n\n"
        "👡 Left Click  = Add Shot\n"
        "👡 Right Click = Add Goal\n"
        "⎵ Space       = Remove Nearest Dot\n"
        "👡 Double Click (Shot Log) = Delete Entry\n"
        "👡 Right Click (Shot Log) = Link / Play Video",
    )

    return frame