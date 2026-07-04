from __future__ import annotations

import tkinter as tk

import ttkbootstrap as tb

from gui.constants import RIGHT_PANEL_WIDTH
from gui.shotlog_view import setup_shotlog_frame

RIGHT_PANEL_SIDE = "right"
RIGHT_PANEL_FILL = "y"
SHOTLOG_RESIZE_HANDLE_WIDTH = 6
SHOTLOG_MIN_WIDTH = 300
SHOTLOG_MAX_WIDTH = 760
SHOTLOG_FLAP_RAIL_WIDTH = 18
SHOTLOG_FLAP_BUTTON_WIDTH = 18
SHOTLOG_FLAP_HEIGHT = 28
SHOTLOG_FLAP_TOP_OFFSET = 10
SHOTLOG_FLAP_EXPANDED_TEXT = ">"
SHOTLOG_FLAP_COLLAPSED_TEXT = "<"
SHOTLOG_RESIZE_CURSOR = "sb_h_double_arrow"
SHOTLOG_FLAP_BG = "#3f8edc"
SHOTLOG_FLAP_ACTIVE_BG = "#2f7ec8"
SHOTLOG_FLAP_FG = "#ffffff"
SHOTLOG_FLAP_FONT = ("Arial", 9, "bold")


def _clamp_width(width: int) -> int:
    return max(SHOTLOG_MIN_WIDTH, min(SHOTLOG_MAX_WIDTH, width))


def _create_panel_container(parent, width: int) -> tb.Frame:
    frame = tb.Frame(parent, width=width)
    frame.pack(side=RIGHT_PANEL_SIDE, fill=RIGHT_PANEL_FILL)
    frame.pack_propagate(False)
    return frame


def _create_flap_button(parent, app, text: str) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=lambda: _toggle_shotlog_panel(app),
        bg=SHOTLOG_FLAP_BG,
        activebackground=SHOTLOG_FLAP_ACTIVE_BG,
        fg=SHOTLOG_FLAP_FG,
        activeforeground=SHOTLOG_FLAP_FG,
        font=SHOTLOG_FLAP_FONT,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        padx=0,
        pady=0,
        takefocus=False,
    )


def _create_expanded_flap(parent, app) -> tb.Frame:
    rail = tb.Frame(parent, width=SHOTLOG_FLAP_RAIL_WIDTH)
    rail.pack(side="left", fill="y")
    rail.pack_propagate(False)

    button = _create_flap_button(rail, app, SHOTLOG_FLAP_EXPANDED_TEXT)
    button.place(
        x=0,
        y=SHOTLOG_FLAP_TOP_OFFSET,
        width=SHOTLOG_FLAP_BUTTON_WIDTH,
        height=SHOTLOG_FLAP_HEIGHT,
    )
    app.shotlog_flap_button = button

    return rail


def _create_collapsed_flap(parent, app) -> tk.Button:
    return _create_flap_button(parent, app, SHOTLOG_FLAP_COLLAPSED_TEXT)


def _show_collapsed_flap(app) -> None:
    app.shotlog_collapsed_flap.place(
        relx=1.0,
        x=0,
        y=SHOTLOG_FLAP_TOP_OFFSET,
        anchor="ne",
        width=SHOTLOG_FLAP_BUTTON_WIDTH,
        height=SHOTLOG_FLAP_HEIGHT,
    )
    app.shotlog_collapsed_flap.lift()


def _hide_collapsed_flap(app) -> None:
    app.shotlog_collapsed_flap.place_forget()


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
    app.right_panel.pack_forget()
    _show_collapsed_flap(app)


def _expand_shotlog_panel(app) -> None:
    app.shotlog_panel_expanded = True
    _hide_collapsed_flap(app)
    app.right_panel.configure(width=app.shotlog_panel_width)

    pack_options = {"side": RIGHT_PANEL_SIDE, "fill": RIGHT_PANEL_FILL}
    if hasattr(app, "center_panel"):
        pack_options["before"] = app.center_panel

    app.right_panel.pack(**pack_options)


def _toggle_shotlog_panel(app) -> None:
    if getattr(app, "shotlog_panel_expanded", True):
        _collapse_shotlog_panel(app)
    else:
        _expand_shotlog_panel(app)


def create_right_panel(parent, app):
    app.shotlog_panel_width = RIGHT_PANEL_WIDTH
    app.shotlog_panel_expanded = True
    app.shotlog_parent = parent

    frame = _create_panel_container(parent, app.shotlog_panel_width)
    app.right_panel = frame
    app.shotlog_expanded_flap = _create_expanded_flap(frame, app)
    app.shotlog_resize_handle = _create_resize_handle(frame, app)
    app.shotlog_content_frame = _create_content_frame(frame, app)
    app.shotlog_collapsed_flap = _create_collapsed_flap(parent, app)

    return frame
