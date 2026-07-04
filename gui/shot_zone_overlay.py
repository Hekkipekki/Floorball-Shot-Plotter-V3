from __future__ import annotations

from pathlib import Path
from tkinter import messagebox

from PIL import Image

from app_paths import PROJECT_ROOT

SHOT_ZONE_DIR = Path(PROJECT_ROOT) / "resources" / "xG"
SHOT_ZONE_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
SHOT_ZONE_DEFAULT_ALPHA = 0.35
SHOT_ZONE_MENU_LABEL_ON = "Hide Shot Zone Overlay"
SHOT_ZONE_MENU_LABEL_OFF = "Show Shot Zone Overlay"


def _find_shot_zone_image() -> Path | None:
    if not SHOT_ZONE_DIR.exists():
        return None

    for path in sorted(SHOT_ZONE_DIR.iterdir()):
        if path.is_file() and path.suffix.lower() in SHOT_ZONE_IMAGE_EXTENSIONS:
            return path

    return None


def load_shot_zone_overlay(app):
    path = _find_shot_zone_image()
    if path is None:
        app.shot_zone_overlay_img = None
        return None

    try:
        image = Image.open(path).convert("RGBA")
        if getattr(app, "img_size", None):
            image = image.resize(app.img_size, Image.Resampling.LANCZOS)
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

    next_value = not app.show_shot_zone_overlay.get()
    if next_value and load_shot_zone_overlay(app) is None:
        messagebox.showwarning(
            "Shot Zone Overlay",
            f"No shot zone image found in:\n{SHOT_ZONE_DIR}\n\nAdd a PNG/JPG/WebP image there and try again.",
        )
        return

    app.show_shot_zone_overlay.set(next_value)
    try:
        app.update_plot()
    except Exception:
        pass
