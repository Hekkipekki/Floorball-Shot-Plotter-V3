"""Small modal progress UI for long-running video export/render actions."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def show_render_progress(app=None, title: str = "Rendering Clip", message: str | None = None):
    """Show a simple indeterminate progress dialog and return it.

    The actual FFmpeg export is still synchronous, but this makes the long task
    visible before the UI thread is occupied. Call ``close_render_progress`` in a
    finally block when the export finishes.
    """

    root = getattr(app, "root", None) or tk._default_root
    if root is None:
        return None

    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.transient(root)
    dialog.resizable(False, False)
    dialog.configure(padx=18, pady=16)
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)

    label = tk.Label(
        dialog,
        text=message or "Exporting and compressing clip...\nThis can take a little while for 4K video.",
        justify="center",
        padx=8,
        pady=8,
    )
    label.pack(fill="x")

    progress = ttk.Progressbar(dialog, mode="indeterminate", length=280)
    progress.pack(fill="x", padx=8, pady=(8, 4))
    progress.start(12)

    try:
        root.update_idletasks()
        width = dialog.winfo_reqwidth()
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
