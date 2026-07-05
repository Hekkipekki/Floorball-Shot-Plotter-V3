from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb

from gui.constants import LEFT_PANEL_WIDTH
from gui.controls import setup_controls

LEFT_PANEL_SIDE = "left"
LEFT_PANEL_FILL = "y"
SCROLL_STEP_UNITS = -1
LEFT_FLAP_RAIL_WIDTH = 18
LEFT_FLAP_BUTTON_WIDTH = 18
LEFT_FLAP_HEIGHT = 28
LEFT_FLAP_TOP_OFFSET = 10
LEFT_FLAP_EXPANDED_TEXT = "<"
LEFT_FLAP_COLLAPSED_TEXT = ">"
LEFT_FLAP_BG = "#3f8edc"
LEFT_FLAP_ACTIVE_BG = "#2f7ec8"
LEFT_FLAP_FG = "#ffffff"
LEFT_FLAP_FONT = ("Arial", 9, "bold")


def _create_fixed_width_panel(parent, width: int) -> tb.Frame:
    frame = tb.Frame(parent, width=width)
    frame.pack(side=LEFT_PANEL_SIDE, fill=LEFT_PANEL_FILL)
    frame.pack_propagate(False)
    return frame


def _create_flap_button(parent, app, text: str) -> tk.Button:
    return tk.Button(
        parent,
        text=text,
        command=lambda: _toggle_left_panel(app),
        bg=LEFT_FLAP_BG,
        activebackground=LEFT_FLAP_ACTIVE_BG,
        fg=LEFT_FLAP_FG,
        activeforeground=LEFT_FLAP_FG,
        font=LEFT_FLAP_FONT,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        padx=0,
        pady=0,
        takefocus=False,
    )


def _create_expanded_flap(parent, app) -> tb.Frame:
    rail = tb.Frame(parent, width=LEFT_FLAP_RAIL_WIDTH)
    rail.pack(side="right", fill="y")
    rail.pack_propagate(False)

    button = _create_flap_button(rail, app, LEFT_FLAP_EXPANDED_TEXT)
    button.place(
        x=0,
        y=LEFT_FLAP_TOP_OFFSET,
        width=LEFT_FLAP_BUTTON_WIDTH,
        height=LEFT_FLAP_HEIGHT,
    )
    app.left_controls_flap_button = button
    return rail


def _create_collapsed_flap(parent, app) -> tk.Button:
    return _create_flap_button(parent, app, LEFT_FLAP_COLLAPSED_TEXT)


def _show_collapsed_flap(app) -> None:
    app.left_controls_collapsed_flap.place(
        x=0,
        y=LEFT_FLAP_TOP_OFFSET,
        anchor="nw",
        width=LEFT_FLAP_BUTTON_WIDTH,
        height=LEFT_FLAP_HEIGHT,
    )
    app.left_controls_collapsed_flap.lift()


def _hide_collapsed_flap(app) -> None:
    app.left_controls_collapsed_flap.place_forget()


def _create_scrollable_controls(parent):
    canvas = tk.Canvas(parent, highlightthickness=0, borderwidth=0)
    scrollbar = tb.Scrollbar(parent, orient="vertical", command=canvas.yview)
    content = tb.Frame(canvas)

    window_id = canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def _update_scroll_region(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _sync_content_width(event):
        canvas.itemconfigure(window_id, width=event.width)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(SCROLL_STEP_UNITS * (event.delta / 120)), "units")

    content.bind("<Configure>", _update_scroll_region)
    canvas.bind("<Configure>", _sync_content_width)
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    return content


def _collapse_left_panel(app) -> None:
    app.left_panel_expanded = False
    app.left_panel.pack_forget()
    _show_collapsed_flap(app)


def _expand_left_panel(app) -> None:
    app.left_panel_expanded = True
    _hide_collapsed_flap(app)
    app.left_panel.configure(width=app.left_panel_width)
    app.left_panel.pack(side=LEFT_PANEL_SIDE, fill=LEFT_PANEL_FILL, before=app.center_panel)


def _toggle_left_panel(app) -> None:
    if getattr(app, "left_panel_expanded", True):
        _collapse_left_panel(app)
    else:
        _expand_left_panel(app)


def create_left_panel(parent, app):
    app.left_panel_width = LEFT_PANEL_WIDTH
    app.left_panel_expanded = True
    app.left_panel_parent = parent

    frame = _create_fixed_width_panel(parent, app.left_panel_width)
    app.left_panel = frame

    app.left_controls_expanded_flap = _create_expanded_flap(frame, app)
    controls_container = _create_scrollable_controls(frame)
    setup_controls(controls_container, app)
    app.left_controls_collapsed_flap = _create_collapsed_flap(parent, app)

    return frame
