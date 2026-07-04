from __future__ import annotations

from pathlib import Path
from tkinter import messagebox

from PIL import Image, ImageDraw, ImageFilter

from app_paths import ASSETS_DIR

SHOT_ZONE_DIR = Path(ASSETS_DIR) / "resources" / "xG"
SHOT_ZONE_IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
SHOT_ZONE_DEFAULT_ALPHA = 0.42
SHOT_ZONE_PREFERRED_FILENAME = "xG Bild Polished.png"
SHOT_ZONE_FALLBACK_FILENAME = "xG Bild.png"
SHOT_ZONE_USE_GENERATED_POLISHED = True

BASE_WIDTH = 1500
BASE_HEIGHT = 1000
ZONE_Y_OFFSET = -70


def _offset_rect(rect):
    x1, y1, x2, y2 = rect
    return x1, y1 + ZONE_Y_OFFSET, x2, y2 + ZONE_Y_OFFSET


def _scaled_rect(rect, size):
    width, height = size
    x1, y1, x2, y2 = rect
    return (
        int(round(x1 / BASE_WIDTH * width)),
        int(round(y1 / BASE_HEIGHT * height)),
        int(round(x2 / BASE_WIDTH * width)),
        int(round(y2 / BASE_HEIGHT * height)),
    )


def _draw_zone(draw: ImageDraw.ImageDraw, rect, size, color, radius: int = 0, *, offset: bool = True) -> None:
    source_rect = _offset_rect(rect) if offset else rect
    scaled = _scaled_rect(source_rect, size)
    if radius:
        draw.rounded_rectangle(scaled, radius=radius, fill=color)
    else:
        draw.rectangle(scaled, fill=color)


def _generate_polished_overlay(size) -> Image.Image:
    width, height = size
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    soft = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(soft)

    # Low-danger upper/deep zone.
    _draw_zone(draw, (20, 250, 1480, 380), size, (104, 221, 53, 210))

    # Lower outside areas and side lanes.
    _draw_zone(draw, (20, 380, 250, 760), size, (155, 217, 107, 190))
    _draw_zone(draw, (1250, 380, 1480, 760), size, (155, 217, 107, 190))
    _draw_zone(draw, (250, 380, 380, 760), size, (73, 161, 34, 205))
    _draw_zone(draw, (1120, 380, 1250, 760), size, (73, 161, 34, 205))

    # Medium/high-danger side channels.
    _draw_zone(draw, (380, 380, 560, 760), size, (165, 61, 61, 205))
    _draw_zone(draw, (940, 380, 1120, 760), size, (165, 61, 61, 205))

    # Central high-danger lane.
    _draw_zone(draw, (560, 380, 940, 690), size, (238, 22, 22, 220))

    # Goal-front / royal-road danger block.
    _draw_zone(draw, (560, 690, 940, 840), size, (115, 13, 13, 230))

    # Behind-goal low-danger band.
    _draw_zone(draw, (20, 760, 1480, 980), size, (184, 226, 162, 160))

    # Soften hard boundaries slightly.
    soft = soft.filter(ImageFilter.GaussianBlur(radius=max(1, int(width * 0.004))))
    overlay.alpha_composite(soft)

    line = ImageDraw.Draw(overlay)
    # Subtle separators/edges to keep zones readable.
    separator = (255, 255, 255, 85)
    for rect in (
        (20, 250, 1480, 380),
        (250, 380, 380, 760),
        (380, 380, 560, 760),
        (560, 380, 940, 690),
        (940, 380, 1120, 760),
        (1120, 380, 1250, 760),
        (560, 690, 940, 840),
        (20, 760, 1480, 980),
    ):
        line.rectangle(_scaled_rect(_offset_rect(rect), size), outline=separator, width=max(1, int(width * 0.002)))

    # Add a light centre highlight so the overlay looks less flat.
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        _scaled_rect(_offset_rect((430, 260, 1070, 860)), size),
        fill=(255, 255, 255, 34),
    )
    overlay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(radius=max(6, int(width * 0.035)))))

    return overlay


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


def _target_size(app) -> tuple[int, int]:
    return getattr(app, "img_size", None) or (BASE_WIDTH, BASE_HEIGHT)


def load_shot_zone_overlay(app):
    try:
        if SHOT_ZONE_USE_GENERATED_POLISHED:
            image = _generate_polished_overlay(_target_size(app))
            app.shot_zone_overlay_img = image
            app.shot_zone_overlay_path = "generated-polished"
            return image

        path = _find_shot_zone_image()
        if path is None:
            app.shot_zone_overlay_img = None
            return None

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
