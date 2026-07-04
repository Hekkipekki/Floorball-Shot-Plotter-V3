from __future__ import annotations

import ttkbootstrap as tb

from gui.constants import RIGHT_PANEL_WIDTH
from gui.shotlog_view import setup_shotlog_frame

RIGHT_PANEL_SIDE = "right"
RIGHT_PANEL_FILL = "y"


def _create_fixed_width_panel(parent, width: int) -> tb.Frame:
    frame = tb.Frame(parent, width=width)
    frame.pack(side=RIGHT_PANEL_SIDE, fill=RIGHT_PANEL_FILL)
    frame.pack_propagate(False)
    return frame


def create_right_panel(parent, app):
    frame = _create_fixed_width_panel(parent, RIGHT_PANEL_WIDTH)
    setup_shotlog_frame(app, frame)
    return frame
