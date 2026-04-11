from __future__ import annotations

import ttkbootstrap as tb

from gui.constants import LEFT_PANEL_WIDTH
from gui.controls import setup_controls


def create_left_panel(parent, app):
    frame = tb.Frame(parent, width=LEFT_PANEL_WIDTH)
    frame.pack(side="left", fill="y")
    frame.pack_propagate(False)

    setup_controls(frame, app)

    return frame