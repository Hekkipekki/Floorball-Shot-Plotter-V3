from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb

from gui.constants import LEFT_PANEL_WIDTH
from gui.controls import setup_controls

LEFT_PANEL_SIDE = "left"
LEFT_PANEL_FILL = "y"
SCROLL_STEP_UNITS = -1


def _create_fixed_width_panel(parent, width: int) -> tb.Frame:
    frame = tb.Frame(parent, width=width)
    frame.pack(side=LEFT_PANEL_SIDE, fill=LEFT_PANEL_FILL)
    frame.pack_propagate(False)
    return frame


def _create_scrollable_controls(parent):
    canvas = tk.Canvas(parent, highlightthickness=0, borderwidth=0)
    scrollbar = tb.Scrollbar(parent, orient="vertical", command=canvas.yview)
    content = tb.Frame(canvas)

    window_id = canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _update_scroll_region(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _sync_content_width(event):
        canvas.itemconfigure(window_id, width=event.width)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(SCROLL_STEP_UNITS * (event.delta / 120)), "units")

    content.bind("<Configure>", _update_scroll_region)
    canvas.bind("<Configure>", _sync_content_width)
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return content


def create_left_panel(parent, app):
    frame = _create_fixed_width_panel(parent, LEFT_PANEL_WIDTH)
    controls_container = _create_scrollable_controls(frame)
    setup_controls(controls_container, app)
    return frame
