from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from utils.video_calibration import (
    CALIBRATION_DONE_TEXT,
    GOPRO_CALIBRATION_POINTS,
    apply_homography,
    compute_homography,
)
from utils.video_player_style import PANEL_BG, TEXT, create_control_button

SHOT_EVENT_TYPE = "shot"
GOAL_EVENT_TYPE = "goal"
VIDEO_PLOT_HELP = "Video Plot: right-click the video, then choose Shot or Goal."
VIDEO_PASS_HELP = "Video Plot: right-click the pass-origin location."


def install_video_plot_adapter(player) -> None:
    player.video_plot_mode = tk.BooleanVar(value=False)
    player.video_calibration_mode = tk.BooleanVar(value=False)
    player.video_calibration_clicks = []
    player.video_calibration_step = 0
    player.video_homography = None
    player.video_area.bind("<Button-3>", lambda event: _on_video_right_click(player, event), add="+")
    player.video_area.bind("<Button-1>", lambda event: _on_video_left_click(player, event), add="+")
    _let_tk_receive_video_mouse_events(player)
    _add_video_plot_controls(player)
    _add_video_plot_hint(player)
    _add_video_calibration_hint(player)


def _let_tk_receive_video_mouse_events(player) -> None:
    try:
        if player.player is not None:
            player.player.video_set_mouse_input(False)
            player.player.video_set_key_input(False)
    except Exception:
        pass


def _add_video_plot_controls(player) -> None:
    try:
        player.timeline.grid_configure(columnspan=10)
        player.save_btn.grid_configure(column=9)
        player.close_small_btn.grid_configure(column=10)
    except Exception:
        pass

    player.video_plot_btn = create_control_button(player.controls, "Plot: OFF", lambda: _toggle_video_plot_mode(player))
    player.video_plot_btn.grid(row=1, column=7, padx=3, pady=(6, 8), sticky="ew")

    player.video_calibration_btn = create_control_button(player.controls, "Calibrate", lambda: _toggle_video_calibration_mode(player))
    player.video_calibration_btn.grid(row=1, column=8, padx=3, pady=(6, 8), sticky="ew")


def _add_video_plot_hint(player) -> None:
    player.video_plot_hint = tk.Label(player, text=VIDEO_PLOT_HELP, bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 9, "bold"), padx=10, pady=5)


def _add_video_calibration_hint(player) -> None:
    player.video_calibration_hint = tk.Label(player, text="", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 9, "bold"), padx=10, pady=5)


def _toggle_video_plot_mode(player) -> None:
    player.video_plot_mode.set(not player.video_plot_mode.get())
    enabled = player.video_plot_mode.get()
    player.video_plot_btn.config(text=f"Plot: {'ON' if enabled else 'OFF'}")
    if enabled:
        if player.video_calibration_mode.get():
            _toggle_video_calibration_mode(player)
        _show_plot_hint(player)
    else:
        player.video_plot_hint.place_forget()


def _toggle_video_calibration_mode(player) -> None:
    player.video_calibration_mode.set(not player.video_calibration_mode.get())
    enabled = player.video_calibration_mode.get()
    player.video_calibration_btn.config(text=f"Cal: {'ON' if enabled else 'OFF'}")
    if enabled:
        if player.video_plot_mode.get():
            _toggle_video_plot_mode(player)
        _start_calibration_sequence(player)
    else:
        player.video_calibration_hint.place_forget()


def _show_plot_hint(player) -> None:
    app = player.app
    if app is not None and getattr(app, "expecting_pass_click", False):
        text = VIDEO_PASS_HELP
    elif getattr(player, "video_homography", None) is not None:
        text = "Video Plot calibrated: right-click the video, then choose Shot or Goal."
    else:
        text = VIDEO_PLOT_HELP
    player.video_plot_hint.config(text=text)
    player.video_plot_hint.place(relx=0.5, y=12, anchor="n")
    player.video_plot_hint.lift()


def _start_calibration_sequence(player) -> None:
    player.video_calibration_clicks = []
    player.video_calibration_step = 0
    player.video_homography = None
    _show_next_calibration_instruction(player)
    messagebox.showinfo("Video Calibration", "Calibration started. Left-click each requested rink landmark in the video.")


def _show_next_calibration_instruction(player) -> None:
    step = player.video_calibration_step
    if step >= len(GOPRO_CALIBRATION_POINTS):
        player.video_calibration_hint.config(text=CALIBRATION_DONE_TEXT)
    else:
        _name, _target, instruction = GOPRO_CALIBRATION_POINTS[step]
        player.video_calibration_hint.config(text=f"Calibration {step + 1}/{len(GOPRO_CALIBRATION_POINTS)}: {instruction}")
    player.video_calibration_hint.place(relx=0.5, y=12, anchor="n")
    player.video_calibration_hint.lift()


def _finish_calibration_sequence(player) -> None:
    homography = compute_homography(player.video_calibration_clicks)
    player.video_homography = homography
    app = player.app
    if app is not None:
        app.video_calibration_points = list(player.video_calibration_clicks)
        app.video_homography = homography
    player.video_calibration_mode.set(False)
    player.video_calibration_btn.config(text="Calibrate")
    player.video_calibration_hint.config(text=CALIBRATION_DONE_TEXT)
    status = "Calibration is active for video plotting." if homography is not None else "Could not compute calibration transform. Fallback plotting remains active."
    messagebox.showinfo("Calibration Complete", f"Captured {len(player.video_calibration_clicks)} calibration points.\n\n{status}")


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


def _video_event_to_normalized_coordinates(player, event) -> tuple[float, float] | None:
    left, top, draw_w, draw_h = _video_content_rect(player)
    if draw_w <= 0 or draw_h <= 0:
        return None
    rel_x = (event.x - left) / draw_w
    rel_y = (event.y - top) / draw_h
    if not (0.0 <= rel_x <= 1.0 and 0.0 <= rel_y <= 1.0):
        return None
    return rel_x, rel_y


def _fallback_normalized_to_plot(player, source_norm: tuple[float, float]) -> tuple[int, int] | None:
    app = player.app
    if app is None or not hasattr(app, "ax"):
        return None
    rel_x, rel_y = source_norm
    xlim = app.ax.get_xlim()
    ylim = app.ax.get_ylim()
    plot_x = xlim[0] + rel_x * (xlim[1] - xlim[0])
    plot_y = ylim[0] + rel_y * (ylim[1] - ylim[0])
    return int(round(plot_x)), int(round(plot_y))


def _video_event_to_plot_coordinates(player, event) -> tuple[int, int] | None:
    source_norm = _video_event_to_normalized_coordinates(player, event)
    if source_norm is None:
        return None
    calibrated = apply_homography(getattr(player, "video_homography", None), source_norm)
    if calibrated is not None:
        return calibrated
    return _fallback_normalized_to_plot(player, source_norm)


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
        app.popup_open = False
        show_phase_dialog(app, x, y, shot_or_goal=shot_or_goal)
    except Exception as exc:
        messagebox.showerror("Video Plot Failed", f"Could not open shot dialog:\n{exc}")


def _clear_pending_pass_data(app) -> None:
    if hasattr(app, "pending_pass_data"):
        del app.pending_pass_data
    app.expecting_pass_click = False


def _add_pending_pass_origin_from_video(player, x: int, y: int) -> None:
    app = player.app
    if app is None:
        return
    data = getattr(app, "pending_pass_data", None)
    if data is None:
        return
    main_x, main_y, phase, situation, shot_type, passer, shooter, event_type = data
    add_event = app.add_goal_event if event_type == GOAL_EVENT_TYPE else app.add_shot_event
    add_event(main_x, main_y, phase, situation, shot_type, passer, shooter, pass_x=x, pass_y=y)
    _clear_pending_pass_data(app)
    _show_plot_hint(player)


def _on_video_left_click(player, event) -> str | None:
    if not getattr(player, "video_calibration_mode", tk.BooleanVar(value=False)).get():
        return None
    source_norm = _video_event_to_normalized_coordinates(player, event)
    fallback_plot = _fallback_normalized_to_plot(player, source_norm) if source_norm is not None else None
    if source_norm is None or fallback_plot is None:
        return "break"
    step = player.video_calibration_step
    if step >= len(GOPRO_CALIBRATION_POINTS):
        return "break"
    name, target_plot, _instruction = GOPRO_CALIBRATION_POINTS[step]
    player.video_calibration_clicks.append({"name": name, "source_norm": source_norm, "fallback_plot": fallback_plot, "target_plot": target_plot})
    player.video_calibration_step += 1
    if player.video_calibration_step >= len(GOPRO_CALIBRATION_POINTS):
        _finish_calibration_sequence(player)
    else:
        _show_next_calibration_instruction(player)
    return "break"


def _on_video_right_click(player, event) -> str | None:
    coords = _video_event_to_plot_coordinates(player, event)
    if coords is None:
        return "break"
    x, y = coords
    app = player.app
    if app is not None and getattr(app, "expecting_pass_click", False):
        _add_pending_pass_origin_from_video(player, x, y)
        return "break"
    if not getattr(player, "video_plot_mode", tk.BooleanVar(value=False)).get():
        return None
    menu = tk.Menu(player, tearoff=0)
    menu.add_command(label=f"Add Shot here ({x}, {y})", command=lambda: _plot_video_point(player, x, y, SHOT_EVENT_TYPE))
    menu.add_command(label=f"Add Goal here ({x}, {y})", command=lambda: _plot_video_point(player, x, y, GOAL_EVENT_TYPE))
    menu.post(event.x_root, event.y_root)
    return "break"
