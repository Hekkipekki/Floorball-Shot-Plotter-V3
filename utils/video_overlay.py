"""Video overlay creation for the embedded VLC player."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from utils.video_player_style import VIDEO_BG
from utils.video_plot_adapter import install_video_plot_adapter
from utils.video_runtime import PLUGINS_DIR, VLC_DIR, VLC_IMPORT_ERROR, vlc
from utils.videoplayer import VLCOverlayWithControls

PLAYBACK_FAILED_TITLE = "Playback Failed"
MISSING_RUNTIME_MESSAGE = "Bundled VLC runtime not available."


def _vlc_runtime_available() -> bool:
    return vlc is not None and VLC_DIR is not None and PLUGINS_DIR is not None


def _show_playback_error() -> None:
    details = VLC_IMPORT_ERROR if VLC_IMPORT_ERROR is not None else MISSING_RUNTIME_MESSAGE
    messagebox.showerror(PLAYBACK_FAILED_TITLE, f"Could not play video:\n{details}")


def _destroy_existing_overlay(app) -> None:
    existing = getattr(app, "video_overlay", None)
    if existing is not None:
        try:
            existing.destroy()
        except Exception:
            pass
        app.video_overlay = None


def _refresh_canvas_frame(app) -> None:
    try:
        app.canvas_frame.update_idletasks()
    except Exception:
        pass


def _create_overlay_frame(app) -> tk.Frame:
    overlay = tk.Frame(app.canvas_frame, bg=VIDEO_BG, bd=0, relief="flat")
    overlay.place(x=0, y=0, relwidth=1.0, relheight=1.0)
    overlay.tkraise()
    return overlay


def _create_player(app, video_path, start, stop, autoplay, on_save_segment):
    player = VLCOverlayWithControls(
        app.video_overlay,
        video_path=video_path,
        start=start,
        stop=stop,
        autoplay=autoplay,
        app=app,
        on_save_segment=on_save_segment,
    )
    install_video_plot_adapter(player)
    return player


def show_video_overlay(
    app,
    video_path: str,
    start: float = 0.0,
    stop: float | None = None,
    *,
    autoplay: bool = True,
    on_save_segment=None,
) -> None:
    if not _vlc_runtime_available():
        _show_playback_error()
        return

    app.popup_open = True
    _destroy_existing_overlay(app)
    _refresh_canvas_frame(app)

    app.video_overlay = _create_overlay_frame(app)
    player = _create_player(app, video_path, start, stop, autoplay, on_save_segment)
    player.pack(fill="both", expand=True)

    app._vlc_player = player
