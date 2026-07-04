"""Helpers for plotting shot locations from the embedded video overlay.

This is intentionally a lightweight beta adapter. It maps the clicked position inside the
currently displayed video area to the existing rink plot coordinate system using normalized
screen position. That gives a practical first step for video-assisted plotting without adding
full camera calibration or xG work.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from utils.video_player_style import PANEL_BG, TEXT, create_control_button

SHOT_EVENT_TYPE = "shot"
GOAL_EVENT_TYPE = "goal"
VIDEO_PLOT_HELP = "Video Plot: right-click the video, then choose Shot or Goal."


def install_video_plot_adapter(player) -> None:
    """Attach video-assisted plotting controls to a VLCOverlayWithControls instance."""
    player.video_plot_mode = tk.BooleanVar(value=False)
    player.video_area.bind("<Button-3>", lambda event: _on_video_right_click(player, event), add="+")

    _let_tk_receive_video_mouse_events(player)
    _add_video_plot_controls(player)
    _add_video_plot_hint(player)


def _let_tk_receive_video_mouse_events(player) -> None:
    try:
        if player.player is not None:
            player.player.video_set_mouse_input(False)
            player.player.video_set_key_input(False)
    except Exception:
        pass


def _add_video_plot_controls(player) -> None:
    try:
        player.timeline.grid_configure(columnspan=9)
        player.save_btn.grid_configure(column=8)
        player.close_small_btn.grid_configure(column=9)
    except Exception:
        pass

    player.video_plot_btn = create_control_button(
        player.controls,
        "Plot: OFF",
        lambda: _toggle_video_plot_mode(player),
    )
    player.video_plot_btn.grid(row=1, column=7, padx=3, pady=(6, 8), sticky="ew")


def _add_video_plot_hint(player) -> None:
    player.video_plot_hint = tk.Label(
        player,
        text=VIDEO_PLOT_HELP,
        bg=PANEL_BG,
        fg=TEXT,
        font=("Segoe UI", 9, "bold"),
        padx=10,
        pady=5,
    )


def _toggle_video_plot_mode(player) -> None:
    player.video_plot_mode.set(not player.video_plot_mode.get())
    enabled = player.video_plot_mode.get()
    player.video_plot_btn.config(text=f"Plot: {'ON' if enabled else 'OFF'}")

    if enabled:
        player.video_plot_hint.place(relx=0.5, y=12, anchor="n")
        player.video_plot_hint.lift()
    else:
        player.video_plot_hint.place_forget()


def _video_content_rect(player) -> tuple[float, float, float, float]:
    area_w = max(1, player.video_area.winfo_width())
    area_h = max(1, player.video_area.winfo_height())

    video_w = 0
    video_h = 0
    try:
        if player.player is not None:
            size = player.player.video_get_size(0)
            if size and len(size) >= 2:
                video_w, video_h = int(size[0]), int(size[1])
    except Exception:
        pass

    if video_w <= 0 or video_h <= 0:
        return 0.0, 0.0, float(area_w), float(area_h)

    scale = min(area_w / video_w, area_h / video_h)
    draw_w = video_w * scale
    draw_h = video_h * scale
    left = (area_w - draw_w) / 2
    top = (area_h - draw_h) / 2
    return left, top, draw_w, draw_h


def _video_event_to_plot_coordinates(player, event) -> tuple[int, int] | None:
    app = player.app
    if app is None or not hasattr(app, "ax"):
        return None

    left, top, draw_w, draw_h = _video_content_rect(player)
    if draw_w <= 0 or draw_h <= 0:
        return None

    rel_x = (event.x - left) / draw_w
    rel_y = (event.y - top) / draw_h
    if not (0.0 <= rel_x <= 1.0 and 0.0 <= rel_y <= 1.0):
        return None

    xlim = app.ax.get_xlim()
    ylim = app.ax.get_ylim()
    plot_x = xlim[0] + rel_x * (xlim[1] - xlim[0])
    plot_y = ylim[0] + rel_y * (ylim[1] - ylim[0])
    return int(round(plot_x)), int(round(plot_y))


def _plot_video_point(player, x: int, y: int, shot_or_goal: str) -> None:
    app = player.app
    if app is None:
        return

    try:
        if player.player is not None and player.player.is_playing():
            player.player.pause()
    except Exception:
        pass

    try:
        from gui.events.event_dialogs import show_phase_dialog

        # The video overlay marks popup_open while active. Temporarily allow the normal
        # shot dialog chain to open from this video-assisted workflow.
        app.popup_open = False
        show_phase_dialog(app, x, y, shot_or_goal=shot_or_goal)
    except Exception as exc:
        messagebox.showerror("Video Plot Failed", f"Could not open shot dialog:\n{exc}")


def _on_video_right_click(player, event) -> str | None:
    if not getattr(player, "video_plot_mode", tk.BooleanVar(value=False)).get():
        return None

    coords = _video_event_to_plot_coordinates(player, event)
    if coords is None:
        return "break"

    x, y = coords
    menu = tk.Menu(player, tearoff=0)
    menu.add_command(
        label=f"Add Shot here ({x}, {y})",
        command=lambda: _plot_video_point(player, x, y, SHOT_EVENT_TYPE),
    )
    menu.add_command(
        label=f"Add Goal here ({x}, {y})",
        command=lambda: _plot_video_point(player, x, y, GOAL_EVENT_TYPE),
    )
    menu.post(event.x_root, event.y_root)
    return "break"
