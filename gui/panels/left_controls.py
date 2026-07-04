from __future__ import annotations

import ttkbootstrap as tb

from gui.constants import LEFT_PANEL_WIDTH
from gui.controls import setup_controls

LEFT_PANEL_SIDE = "left"
LEFT_PANEL_FILL = "y"


def _create_fixed_width_panel(parent, width: int) -> tb.Frame:
    frame = tb.Frame(parent, width=width)
    frame.pack(side=LEFT_PANEL_SIDE, fill=LEFT_PANEL_FILL)
    frame.pack_propagate(False)
    return frame


def create_left_panel(parent, app):
    frame = _create_fixed_width_panel(parent, LEFT_PANEL_WIDTH)
    setup_controls(frame, app)
    return frame
