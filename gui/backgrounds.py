from __future__ import annotations

from assets import get_default_background, list_background_files
from gui.layout import update_background_menu


def get_available_backgrounds(app):
    return list_background_files()


def init_background_files(app):
    app.bg_files = get_available_backgrounds(app)

    default_bg = get_default_background()

    if default_bg:
        app.bg_choice.set(default_bg)
        app.selected_background.set(default_bg)
    else:
        app.bg_choice.set("")
        app.selected_background.set("")

    update_background_menu(app)


def set_background(app, bg_name):
    if bg_name not in app.bg_files:
        return

    if app.selected_background.get() == bg_name:
        return

    app.selected_background.set(bg_name)

    from gui.plot_background import refresh_image
    refresh_image(app)