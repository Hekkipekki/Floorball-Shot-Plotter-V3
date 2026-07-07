from __future__ import annotations

import os
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

from gui.shotlog_video import CLIP_FILETYPES, VIDEO_FILETYPES
from paths import VIDEOS_DIR, ensure_data_dirs
from utils.render_progress import close_render_progress, show_render_progress, update_render_progress
from utils.video_clip_exporter import export_local_segment
from utils.video_overlay import show_video_overlay
from utils.youtube_resolver import OnlineVideoError, resolve_online_video

VIDEO_MENU_OPEN_TITLE = "Open Video Clip"
VIDEO_MISSING_TITLE = "Video Missing"
VIDEO_MISSING_MESSAGE = "Video file could not be found."


def _default_clip_name(source_path: str, start: float, stop: float | None) -> str:
    source_stem = Path(source_path).stem or "video_clip"
    start_label = int(max(0.0, float(start or 0.0)))
    stop_label = "end" if stop is None else int(max(0.0, float(stop)))
    return f"{source_stem}_{start_label}s-{stop_label}s.mp4"


def _export_standalone_local_clip(app, path: str, start: float, stop: float | None) -> None:
    ensure_data_dirs()
    output_path = filedialog.asksaveasfilename(
        title="Export Short Clip",
        initialdir=str(VIDEOS_DIR),
        initialfile=_default_clip_name(path, start, stop),
        defaultextension=".mp4",
        filetypes=CLIP_FILETYPES,
    )
    if not output_path:
        return

    progress = show_render_progress(app, message="Exporting 1080p analysis clip...\nPlease wait.")
    try:
        export_local_segment(
            path,
            output_path,
            start=start,
            stop=stop,
            progress_callback=lambda fraction, rendered, total: update_render_progress(progress, fraction, rendered, total),
        )
    finally:
        close_render_progress(progress)
    messagebox.showinfo("Clip Exported", "The shorter 1080p clip was exported successfully.")


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
        on_export_segment=lambda start, stop: _export_standalone_local_clip(app, path, start, stop),
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
