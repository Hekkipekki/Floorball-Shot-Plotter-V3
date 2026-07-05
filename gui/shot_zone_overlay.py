from __future__ import annotations

from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageEnhance

from app_paths import ASSETS_DIR

SHOT_ZONE_DIR = Path(ASSETS_DIR) / "resources" / "xG"
SHOT_ZONE_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
SHOT_ZONE_DEFAULT_ALPHA = 0.62
SHOT_ZONE_PREFERRED_FILENAME = "Danger Zones.png"
SHOT_ZONE_FALLBACK_FILENAME = "xG Bild.png"


def _find_shot_zone_image() -> Path | None:
    preferred = SHOT_ZONE_DIR / SHOT_ZONE_PREFERRED_FILENAME
    if preferred.exists():
        return preferred

    fallback = SHOT_ZONE_DIR / SHOT_ZONE_FALLBACK_FILENAME
    if fallback.exists():
        return fallback

    if not SHOT_ZONE_DIR.exists():
        return None

    for path in sorted(SHOT_ZONE_DIR.iterdir()):
        if path.is_file() and path.suffix.lower() in SHOT_ZONE_IMAGE_EXTENSIONS:
            return path

    return None


def _target_size(app) -> tuple[int, int] | None:
    return getattr(app, "img_size", None)


def _make_transparent(image: Image.Image, alpha: float = SHOT_ZONE_DEFAULT_ALPHA) -> Image.Image:
    image = image.convert("RGBA")
    r, g, b, a = image.split()
    a = ImageEnhance.Brightness(a).enhance(alpha)
    image.putalpha(a)
    return image


def _prepare_danger_zone_overlay(image: Image.Image) -> Image.Image:
    # Preserve the Photoshop asset exactly. Only apply transparency.
    return _make_transparent(image)


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

        image = _prepare_danger_zone_overlay(image)
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
            f"No shot zone image found in:\n{SHOT_ZONE_DIR}\n\nAdd Danger Zones.png or another PNG/JPG/WebP image there and try again.",
        )
        return

    try:
        app.update_plot()
    except Exception:
        pass
