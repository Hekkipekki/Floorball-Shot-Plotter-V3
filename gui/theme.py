from __future__ import annotations

import ttkbootstrap as tb

from gui.constants import DEFAULT_THEME


def apply_theme(app, theme_name: str = DEFAULT_THEME):
    """
    Create and apply the ttkbootstrap theme for the app.
    """
    app.style = tb.Style()
    app.style.theme_use(theme_name)