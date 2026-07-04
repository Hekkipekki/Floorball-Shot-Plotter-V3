from __future__ import annotations

import os
from tkinter import filedialog, messagebox

EXPORT_DEFAULT_EXTENSION = ".png"
EXPORT_FILETYPES = [("PNG Image", "*.png")]
EXPORT_DPI = 300
EXPORT_BBOX = "tight"
EXPORT_DIALOG_TITLE = "Export Plot As Image"


def _ask_export_path():
    return filedialog.asksaveasfilename(
        defaultextension=EXPORT_DEFAULT_EXTENSION,
        filetypes=EXPORT_FILETYPES,
        title=EXPORT_DIALOG_TITLE,
    )


def _show_export_success(file_path: str) -> None:
    messagebox.showinfo(
        "Image Saved",
        f"Exported plot to:\n{os.path.basename(file_path)}",
    )


def export_figure_as_image(app, figure):
    file_path = _ask_export_path()
    if not file_path:
        return

    figure.savefig(file_path, bbox_inches=EXPORT_BBOX, dpi=EXPORT_DPI)
    _show_export_success(file_path)
