"""Progress UI for long-running video export/render actions."""

from __future__ import annotations

import time
import tkinter as tk
from tkinter import ttk


def _format_seconds(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "--:--"
    seconds = int(round(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def show_render_progress(app=None, title: str = "Rendering Clip", message: str | None = None):
    root = getattr(app, "root", None) or tk._default_root
    if root is None:
        return None

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.transient(root)
    dialog.resizable(False, False)
    dialog.configure(padx=18, pady=16)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    dialog._render_started_at = time.monotonic()

    dialog.message_label = tk.Label(
        dialog,
        text=message or "Exporting and compressing clip...",
        justify="center",
        padx=8,
        pady=6,
    )
    dialog.message_label.pack(fill="x")

    dialog.status_label = tk.Label(
        dialog,
        text="Elapsed: 00:00 | ETA: calculating...",
        justify="center",
        padx=8,
        pady=4,
    )
    dialog.status_label.pack(fill="x")

    dialog.progress = ttk.Progressbar(dialog, mode="determinate", length=320, maximum=100)
    dialog.progress.pack(fill="x", padx=8, pady=(8, 4))

    try:
        root.update_idletasks()
        width = max(380, dialog.winfo_reqwidth())
        height = dialog.winfo_reqheight()
        x = root.winfo_rootx() + max(0, (root.winfo_width() - width) // 2)
        y = root.winfo_rooty() + max(0, (root.winfo_height() - height) // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.lift()
        dialog.grab_set()
        root.update()
    except Exception:
        pass

    return dialog


def update_render_progress(dialog, fraction: float | None = None, rendered_seconds: float | None = None, total_seconds: float | None = None) -> None:
    if dialog is None:
        return

    try:
        elapsed = time.monotonic() - getattr(dialog, "_render_started_at", time.monotonic())
        percent_text = ""
        eta_text = "calculating..."

        if fraction is not None:
            fraction = max(0.0, min(1.0, float(fraction)))
            dialog.progress["value"] = fraction * 100
            percent_text = f" | {fraction * 100:.0f}%"
            if fraction > 0.02:
                eta_seconds = max(0.0, elapsed * (1.0 - fraction) / fraction)
                eta_text = _format_seconds(eta_seconds)

        clip_text = ""
        if rendered_seconds is not None and total_seconds:
            clip_text = f" | Clip: {_format_seconds(rendered_seconds)} / {_format_seconds(total_seconds)}"

        dialog.status_label.config(
            text=f"Elapsed: {_format_seconds(elapsed)} | ETA: {eta_text}{percent_text}{clip_text}"
        )
        dialog.update_idletasks()
        dialog.update()
    except Exception:
        pass


def close_render_progress(dialog) -> None:
    if dialog is None:
        return
    try:
        dialog.grab_release()
    except Exception:
        pass
    try:
        dialog.destroy()
    except Exception:
        pass
