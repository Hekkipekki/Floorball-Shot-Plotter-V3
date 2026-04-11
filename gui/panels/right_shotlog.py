from __future__ import annotations

import ttkbootstrap as tb

from gui.constants import RIGHT_PANEL_WIDTH
from gui.shotlog_view import setup_shotlog_frame


def create_right_panel(parent, app):
    frame = tb.Frame(parent, width=RIGHT_PANEL_WIDTH)
    frame.pack(side="right", fill="y")
    frame.pack_propagate(False)

    setup_shotlog_frame(app, frame)

    return frame