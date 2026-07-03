from __future__ import annotations

import os

from PIL import Image, ImageTk

from app_paths import MATCHES_DIR, PROJECT_ROOT
from assets import get_icon_path
from gui.plot_interactions import connect_hover_events
from gui.point_removal import remove_nearest_point

APP_ICON_FILENAME = "Icon.ico"
TRASH_ICON_FILENAME = "trash.png"


def _maximize_window(app) -> None:
    try:
        app.root.state("zoomed")
    except Exception:
        width = app.root.winfo_screenwidth()
        height = app.root.winfo_screenheight()
        app.root.geometry(f"{width}x{height}+0+0")


def configure_window(app):
    _maximize_window(app)
    app.root.bind("<Escape>", lambda e: app.root.state("normal"))


def configure_paths(app):
    app.project_root = PROJECT_ROOT
    os.makedirs(MATCHES_DIR, exist_ok=True)
    app.matches_dir = MATCHES_DIR


def _load_window_icon(app) -> None:
    icon_path = get_icon_path(APP_ICON_FILENAME)
    if os.path.exists(icon_path):
        try:
            app.root.iconbitmap(icon_path)
        except Exception:
            pass


def _load_trash_icon(app) -> None:
    trash_path = get_icon_path(TRASH_ICON_FILENAME)
    try:
        img = Image.open(trash_path).convert("RGBA")
        app.trash_icon = ImageTk.PhotoImage(img)
    except Exception:
        app.trash_icon = None


def load_icons(app):
    _load_window_icon(app)
    _load_trash_icon(app)


def bind_events(app):
    app.root.bind_all("<space>", lambda e: remove_nearest_point(app, e))
    app.root.bind_all("<Key-space>", lambda e: remove_nearest_point(app, e))
    connect_hover_events(app)
