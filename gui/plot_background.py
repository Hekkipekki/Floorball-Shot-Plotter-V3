from __future__ import annotations

import os

import numpy as np
from PIL import Image

from assets import get_background_path


def set_default_canvas_dimensions(app):
    app.img = None
    app.img_size = (1500, 1000)
    app.img_extent = [0, 1500, 1000, 0]
    app.original_xlim = (0, 1500)
    app.original_ylim = (1000, 0)


def load_image(app):
    """
    Load the selected background image into app.img and update plot bounds.

    This function only loads state.
    It does NOT redraw the plot.
    """
    selected = app.selected_background.get().strip() if hasattr(app, "selected_background") else ""
    if not selected:
        print("⚠️ No background selected.")
        set_default_canvas_dimensions(app)
        return

    path = get_background_path(selected)

    try:
        if not os.path.exists(path):
            print(f"⚠️ Background not found: {path}")
            set_default_canvas_dimensions(app)
            return

        original = Image.open(path).convert("RGB")
        width, height = original.size

        scale = 1.0
        new_size = (int(width * scale), int(height * scale))
        original = original.resize(new_size, Image.Resampling.LANCZOS)

        app.img = np.array(original)
        app.img_size = new_size
        app.img_extent = [0, new_size[0], new_size[1], 0]
        app.original_xlim = (0, new_size[0])
        app.original_ylim = (new_size[1], 0)

    except Exception as e:
        print(f"⚠️ Failed to load background: {e}")
        set_default_canvas_dimensions(app)


def refresh_image(app):
    """
    Full background refresh flow:
    1. load image state
    2. redraw plot once
    """
    from gui.plot_rendering import update_plot

    load_image(app)
    update_plot(app)