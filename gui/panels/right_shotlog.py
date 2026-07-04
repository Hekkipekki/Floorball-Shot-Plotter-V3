from __future__ import annotations

import tkinter as tk

import ttkbootstrap as tb

from gui.constants import RIGHT_PANEL_WIDTH
from gui.shotlog_view import setup_shotlog_frame

RIGHT_PANEL_SIDE = "right"
RIGHT_PANEL_FILL = "y"
SHOTLOG_COLLAPSED_WIDTH = 28
SHOTLOG_RESIZE_HANDLE_WIDTH = 6
SHOTLOG_MIN_WIDTH = 300
SHOTLOG_MAX_WIDTH = 760
SHOTLOG_FLAP_EXPANDED_TEXT = "▶"
SHOTLOG_FLAP_COLLAPSED_TEXT = "◀"
SHOTLOG_RESIZE_CURSOR = "sb_h_double_arrow"


def _clamp_width(width: int) -> int:
    return max(SHOTLOG_MIN_WIDTH, min(SHOTLOG_MAX_WIDTH, width))


def _create_panel_container(parent, width: int) -> tb.Frame:
    frame = tb.Frame(parent, width=width)
    frame.pack(side=RIGHT_PANEL_SIDE, fill=RIGHT_PANEL_FILL)
    frame.pack_propagate(False)
    return frame


def _create_flap_button(parent, app) -> tb.Button:
    button = tb.Button(
        parent,
        text=SHOTLOG_FLAP_EXPANDED_TEXT,
        width=2,
        bootstyle="secondary-outline",
        command=lambda: _toggle_shotlog_panel(app),
    )
    button.pack(side="left", fill="y")
    return button


def _create_resize_handle(parent, app) -> tb.Frame:
    handle = tb.Frame(parent, width=SHOTLOG_RESIZE_HANDLE_WIDTH, cursor=SHOTLOG_RESIZE_CURSOR)
    handle.pack(side="left", fill="y")
    handle.pack_propagate(False)

    handle.bind("<ButtonPress-1>", lambda event: _start_resize(app, event))
    handle.bind("<B1-Motion>", lambda event: _resize_panel(app, event))
    handle.bind("<ButtonRelease-1>", lambda event: _finish_resize(app))

    return handle


def _create_content_frame(parent, app) -> tb.Frame:
    content = tb.Frame(parent)
    content.pack(side="left", fill="both", expand=True)
    setup_shotlog_frame(app, content)
    return content


def _start_resize(app, event: tk.Event) -> None:
    if not getattr(app, "shotlog_panel_expanded", True):
        return

    app._shotlog_resize_start_x = event.x_root
    app._shotlog_resize_start_width = app.shotlog_panel_width


def _resize_panel(app, event: tk.Event) -> None:
    if not getattr(app, "shotlog_panel_expanded", True):
        return

    start_x = getattr(app, "_shotlog_resize_start_x", event.x_root)
    start_width = getattr(app, "_shotlog_resize_start_width", app.shotlog_panel_width)

    # The shot log is docked on the right, so dragging the left border left makes it wider.
    delta_x = event.x_root - start_x
    new_width = _clamp_width(start_width - delta_x)

    app.shotlog_panel_width = new_width
    app.right_panel.configure(width=new_width)


def _finish_resize(app) -> None:
    app._shotlog_resize_start_x = None
    app._shotlog_resize_start_width = app.shotlog_panel_width


def _collapse_shotlog_panel(app) -> None:
    app.shotlog_panel_expanded = False
    app.shotlog_resize_handle.pack_forget()
    app.shotlog_content_frame.pack_forget()
    app.shotlog_flap_button.configure(text=SHOTLOG_FLAP_COLLAPSED_TEXT)
    app.right_panel.configure(width=SHOTLOG_COLLAPSED_WIDTH)


def _expand_shotlog_panel(app) -> None:
    app.shotlog_panel_expanded = True
    app.shotlog_resize_handle.pack(side="left", fill="y")
    app.shotlog_content_frame.pack(side="left", fill="both", expand=True)
    app.shotlog_flap_button.configure(text=SHOTLOG_FLAP_EXPANDED_TEXT)
    app.right_panel.configure(width=app.shotlog_panel_width)


def _toggle_shotlog_panel(app) -> None:
    if getattr(app, "shotlog_panel_expanded", True):
        _collapse_shotlog_panel(app)
    else:
        _expand_shotlog_panel(app)


def create_right_panel(parent, app):
    app.shotlog_panel_width = RIGHT_PANEL_WIDTH
    app.shotlog_panel_expanded = True

    frame = _create_panel_container(parent, app.shotlog_panel_width)
    app.right_panel = frame
    app.shotlog_flap_button = _create_flap_button(frame, app)
    app.shotlog_resize_handle = _create_resize_handle(frame, app)
    app.shotlog_content_frame = _create_content_frame(frame, app)

    return frame
