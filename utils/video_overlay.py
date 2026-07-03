"""Video overlay creation for the embedded VLC player."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from utils.video_runtime import PLUGINS_DIR, VLC_DIR, VLC_IMPORT_ERROR, vlc
from utils.videoplayer import VLCOverlayWithControls


def show_video_overlay(
    app,
    video_path: str,
    start: float = 0.0,
    stop: float | None = None,
    *,
    autoplay: bool = True,
    on_save_segment=None,
) -> None:
    if vlc is None or VLC_DIR is None or PLUGINS_DIR is None:
        details = VLC_IMPORT_ERROR if VLC_IMPORT_ERROR is not None else "Bundled VLC runtime not available."
        messagebox.showerror("Playback Failed", f"Could not play video:\n{details}")
        return

    app.popup_open = True

    existing = getattr(app, "video_overlay", None)
    if existing is not None:
        try:
            existing.destroy()
        except Exception:
            pass
        app.video_overlay = None

    try:
        app.canvas_frame.update_idletasks()
    except Exception:
        pass

    app.video_overlay = tk.Frame(app.canvas_frame, bg="#0b0f14", bd=0, relief="flat")
    app.video_overlay.place(x=0, y=0, relwidth=1.0, relheight=1.0)
    app.video_overlay.tkraise()

    player = VLCOverlayWithControls(
        app.video_overlay,
        video_path=video_path,
        start=start,
        stop=stop,
        autoplay=autoplay,
        app=app,
        on_save_segment=on_save_segment,
    )
    player.pack(fill="both", expand=True)

    app._vlc_player = player
