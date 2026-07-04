from __future__ import annotations

import tkinter.font as tkfont

import ttkbootstrap as tb

from gui.constants import (
    APP_FONT_FAMILY,
    APP_FONT_SIZE,
    APP_FONT_SIZE_LARGE,
    APP_FONT_SIZE_SMALL,
    APP_FONT_SIZE_TITLE,
    DEFAULT_THEME,
    SHOTLOG_FONT_FAMILY,
    SHOTLOG_FONT_SIZE,
    SHOTLOG_HEADING_FONT_SIZE,
    SHOTLOG_ROW_HEIGHT,
)


def _create_style() -> tb.Style:
    return tb.Style()


def _configure_tk_fonts(root) -> None:
    font_settings = {
        "TkDefaultFont": (APP_FONT_FAMILY, APP_FONT_SIZE),
        "TkTextFont": (APP_FONT_FAMILY, APP_FONT_SIZE),
        "TkMenuFont": (APP_FONT_FAMILY, APP_FONT_SIZE),
        "TkHeadingFont": (APP_FONT_FAMILY, APP_FONT_SIZE_LARGE, "bold"),
        "TkCaptionFont": (APP_FONT_FAMILY, APP_FONT_SIZE_SMALL),
        "TkSmallCaptionFont": (APP_FONT_FAMILY, APP_FONT_SIZE_SMALL),
    }

    for font_name, font_value in font_settings.items():
        try:
            tkfont.nametofont(font_name).configure(family=font_value[0], size=font_value[1])
            if len(font_value) > 2:
                tkfont.nametofont(font_name).configure(weight=font_value[2])
        except Exception:
            pass


def _configure_ttk_styles(style: tb.Style) -> None:
    style.configure("TButton", font=(APP_FONT_FAMILY, APP_FONT_SIZE, "bold"), padding=(8, 5))
    style.configure("TLabel", font=(APP_FONT_FAMILY, APP_FONT_SIZE))
    style.configure("TLabelframe.Label", font=(APP_FONT_FAMILY, APP_FONT_SIZE_TITLE, "bold"))
    style.configure("TCheckbutton", font=(APP_FONT_FAMILY, APP_FONT_SIZE))
    style.configure("TMenubutton", font=(APP_FONT_FAMILY, APP_FONT_SIZE, "bold"), padding=(8, 5))
    style.configure("TCombobox", font=(APP_FONT_FAMILY, APP_FONT_SIZE), padding=(4, 3))
    style.configure("Treeview", font=(SHOTLOG_FONT_FAMILY, SHOTLOG_FONT_SIZE), rowheight=SHOTLOG_ROW_HEIGHT)
    style.configure("Treeview.Heading", font=(APP_FONT_FAMILY, SHOTLOG_HEADING_FONT_SIZE, "bold"))


def apply_theme(app, theme_name: str = DEFAULT_THEME):
    """
    Create and apply the ttkbootstrap theme for the app.
    """
    app.style = _create_style()
    app.style.theme_use(theme_name)
    _configure_tk_fonts(app.root)
    _configure_ttk_styles(app.style)
