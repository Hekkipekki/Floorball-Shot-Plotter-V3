from __future__ import annotations

from pathlib import Path
from tkinter import messagebox

import numpy as np
from PIL import Image, ImageFilter

from app_paths import ASSETS_DIR

SHOT_ZONE_DIR = Path(ASSETS_DIR) / "resources" / "xG"
SHOT_ZONE_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
SHOT_ZONE_DEFAULT_ALPHA = 1.0
SHOT_ZONE_PREFERRED_FILENAME = "xG Bild.png"

# Use the real 918x612 source image as the geometry reference, then clean it into
# a transparent overlay. This preserves alignment with the current background image.
ZONE_ALPHA_GREEN = 95
ZONE_ALPHA_GREEN_STRONG = 115
ZONE_ALPHA_RED = 120
ZONE_ALPHA_RED_STRONG = 150
SATURATION_THRESHOLD = 25
CHANNEL_DOMINANCE = 1.05


def _find_shot_zone_image() -> Path | None:
    preferred = SHOT_ZONE_DIR / SHOT_ZONE_PREFERRED_FILENAME
    if preferred.exists():
        return preferred

    if not SHOT_ZONE_DIR.exists():
        return None

    for path in sorted(SHOT_ZONE_DIR.iterdir()):
        if path.is_file() and path.suffix.lower() in SHOT_ZONE_IMAGE_EXTENSIONS:
            return path

    return None


def _target_size(app) -> tuple[int, int] | None:
    return getattr(app, "img_size", None)


def _zone_masks(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]
    saturation = rgb.max(axis=2) - rgb.min(axis=2)

    red_mask = (
        (red > green * CHANNEL_DOMINANCE)
        & (red > blue * CHANNEL_DOMINANCE)
        & (red > 70)
        & (saturation > SATURATION_THRESHOLD)
    )
    strong_red_mask = red_mask & (red > 150) & (green < 90)

    green_mask = (
        (green > red * CHANNEL_DOMINANCE)
        & (green > blue * CHANNEL_DOMINANCE)
        & (green > 80)
        & (saturation > SATURATION_THRESHOLD)
    )
    strong_green_mask = green_mask & ((green - red) > 70)
    return red_mask, strong_red_mask, green_mask, strong_green_mask


def _polish_source_overlay(image: Image.Image) -> Image.Image:
    source = image.convert("RGBA")
    arr = np.asarray(source).astype(np.float32)
    rgb = arr[:, :, :3]

    red_mask, strong_red_mask, green_mask, strong_green_mask = _zone_masks(rgb)
    out = np.zeros_like(arr, dtype=np.uint8)

    # Soft greens for lower-danger zones.
    out[green_mask, 0] = 135
    out[green_mask, 1] = 205
    out[green_mask, 2] = 105
    out[green_mask, 3] = ZONE_ALPHA_GREEN

    out[strong_green_mask, 0] = 78
    out[strong_green_mask, 1] = 170
    out[strong_green_mask, 2] = 56
    out[strong_green_mask, 3] = ZONE_ALPHA_GREEN_STRONG

    # Softer reds for danger zones.
    out[red_mask, 0] = 205
    out[red_mask, 1] = 74
    out[red_mask, 2] = 74
    out[red_mask, 3] = ZONE_ALPHA_RED

    out[strong_red_mask, 0] = 225
    out[strong_red_mask, 1] = 36
    out[strong_red_mask, 2] = 36
    out[strong_red_mask, 3] = ZONE_ALPHA_RED_STRONG

    polished = Image.fromarray(out, "RGBA")
    # Tiny blur removes harsh jagged source edges without changing the underlying geometry.
    return polished.filter(ImageFilter.GaussianBlur(radius=0.7))


def load_shot_zone_overlay(app):
    path = _find_shot_zone_image()
    if path is None:
        app.shot_zone_overlay_img = None
        return None

    try:
        image = Image.open(path).convert("RGBA")
        target_size = _target_size(app)
        if target_size:
            image = image.resize(target_size, Image.Resampling.LANCZOS)

        image = _polish_source_overlay(image)
        app.shot_zone_overlay_img = image
        app.shot_zone_overlay_path = path
        return image
    except Exception as exc:
        app.shot_zone_overlay_img = None
        messagebox.showerror("Shot Zone Overlay", f"Could not load shot zone image:\n{exc}")
        return None


def shot_zone_overlay_enabled(app) -> bool:
    return bool(getattr(app, "show_shot_zone_overlay", None) and app.show_shot_zone_overlay.get())


def toggle_shot_zone_overlay(app) -> None:
    if not hasattr(app, "show_shot_zone_overlay"):
        return

    enabled = app.show_shot_zone_overlay.get()
    if enabled and load_shot_zone_overlay(app) is None:
        app.show_shot_zone_overlay.set(False)
        messagebox.showwarning(
            "Shot Zone Overlay",
            f"No shot zone image found in:\n{SHOT_ZONE_DIR}\n\nAdd a PNG/JPG/WebP image there and try again.",
        )
        return

    try:
        app.update_plot()
    except Exception:
        pass
