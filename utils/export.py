from __future__ import annotations

import os
from tkinter import filedialog, messagebox


def export_figure_as_image(app, figure):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png")],
        title="Export Plot As Image",
    )

    if file_path:
        figure.savefig(file_path, bbox_inches="tight", dpi=300)
        messagebox.showinfo(
            "Image Saved",
            f"Exported plot to:\n{os.path.basename(file_path)}",
        )