from __future__ import annotations

import os
from tkinter import filedialog, messagebox

from gui.shotlog_video import VIDEO_FILETYPES
from utils.video_overlay import show_video_overlay


VIDEO_MENU_OPEN_TITLE = "Open Video Clip"
VIDEO_MISSING_TITLE = "Video Missing"
VIDEO_MISSING_MESSAGE = "Video file could not be found."


def open_video_clip(app) -> None:
    """Open a local video in the center overlay without requiring a logged shot first."""
    path = filedialog.askopenfilename(
        title=VIDEO_MENU_OPEN_TITLE,
        filetypes=VIDEO_FILETYPES,
    )
    if not path:
        return

    if not os.path.exists(path):
        messagebox.showwarning(VIDEO_MISSING_TITLE, VIDEO_MISSING_MESSAGE)
        return

    show_video_overlay(
        app,
        path,
        start=0.0,
        stop=None,
        autoplay=True,
        on_save_segment=None,
    )
