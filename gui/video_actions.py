from __future__ import annotations

import os
from tkinter import filedialog, messagebox, simpledialog

from gui.async_clip_export import export_standalone_local_clip_async
from gui.shotlog_video import VIDEO_FILETYPES
from utils.video_overlay import show_video_overlay
from utils.youtube_resolver import OnlineVideoError, resolve_online_video

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
        on_export_segment=lambda start, stop: export_standalone_local_clip_async(app, path, start, stop),
        video_source_id=path,
    )


def open_youtube_video(app) -> None:
    """Resolve a YouTube/online URL and open it in the embedded VLC overlay."""
    url = simpledialog.askstring("Open YouTube / Online Video", "Enter YouTube / video URL:")
    if not url:
        return

    try:
        resolved = resolve_online_video(url)
    except OnlineVideoError as exc:
        messagebox.showerror("Online Video Failed", str(exc))
        return

    show_video_overlay(
        app,
        resolved.playback_url,
        start=0.0,
        stop=None,
        autoplay=True,
        on_save_segment=None,
        on_export_segment=None,
        video_source_id=url,
    )
