from __future__ import annotations

import os

import numpy as np
from PIL import Image

from assets import get_background_path

DEFAULT_CANVAS_SIZE = (1500, 1000)
DEFAULT_IMAGE_EXTENT = [0, 1500, 1000, 0]
DEFAULT_XLIM = (0, 1500)
DEFAULT_YLIM = (1000, 0)
IMAGE_SCALE = 1.0


def set_default_canvas_dimensions(app):
    app.img = None
    app.img_size = DEFAULT_CANVAS_SIZE
    app.img_extent = DEFAULT_IMAGE_EXTENT.copy()
    app.original_xlim = DEFAULT_XLIM
    app.original_ylim = DEFAULT_YLIM


def _selected_background(app) -> str:
    if not hasattr(app, "selected_background"):
        return ""
    return app.selected_background.get().strip()


def _resize_background(image: Image.Image):
    width, height = image.size
    size = (int(width * IMAGE_SCALE), int(height * IMAGE_SCALE))
    return image.resize(size, Image.Resampling.LANCZOS), size


def _apply_background_image(app, image: Image.Image, size) -> None:
    app.img = np.array(image)
    app.img_size = size
    app.img_extent = [0, size[0], size[1], 0]
    app.original_xlim = (0, size[0])
    app.original_ylim = (size[1], 0)


def load_image(app):
    """
    Load the selected background image into app.img and update plot bounds.

    This function only loads state.
    It does NOT redraw the plot.
    """
    selected = _selected_background(app)
    if not selected:
        print("No background selected.")
        set_default_canvas_dimensions(app)
        return

    path = get_background_path(selected)

    try:
        if not os.path.exists(path):
            print(f"Background not found: {path}")
            set_default_canvas_dimensions(app)
            return

        image = Image.open(path).convert("RGB")
        image, size = _resize_background(image)
        _apply_background_image(app, image, size)

    except Exception as e:
        print(f"Failed to load background: {e}")
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
