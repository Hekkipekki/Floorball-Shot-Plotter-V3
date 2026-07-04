from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb

from gui.panels.left_controls import create_left_panel
from gui.panels.center_plot import create_center_plot
from gui.panels.right_shotlog import create_right_panel
from gui.panels.controls.heatmap_controls import show_heatmap_settings_window
from gui.theme import apply_theme
from gui.video_actions import open_video_clip

FILE_MENU_COMMANDS = [
    ("Save CSV", "save_csv"),
    ("Load CSV", "load_csv"),
    None,
    ("Export Image", "export_plot"),
]


VIDEO_MENU_COMMANDS = [
    ("Open Video Clip...", open_video_clip),
]


def _create_main_frame(root) -> tb.Frame:
    frame = tb.Frame(root)
    frame.pack(fill="both", expand=True)
    return frame


def _create_app_panels(app, main_frame: tb.Frame) -> None:
    # Important: create side panels first, then center last
    app.left_panel = create_left_panel(main_frame, app)
    app.right_panel = create_right_panel(main_frame, app)
    app.center_panel = create_center_plot(main_frame, app)


def _finish_initial_ui_state(app) -> None:
    app.update_match_dropdown()
    app.update_stats_filtered()


def setup_ui(app):
    apply_theme(app)

    main_frame = _create_main_frame(app.root)
    _create_app_panels(app, main_frame)
    create_menu_bar(app)
    _finish_initial_ui_state(app)


def _create_file_menu(app, menubar: tk.Menu) -> tk.Menu:
    file_menu = tk.Menu(menubar, tearoff=0)

    for command in FILE_MENU_COMMANDS:
        if command is None:
            file_menu.add_separator()
            continue

        label, callback_name = command
        file_menu.add_command(label=label, command=getattr(app, callback_name))

    return file_menu


def _create_video_menu(app, menubar: tk.Menu) -> tk.Menu:
    video_menu = tk.Menu(menubar, tearoff=0)

    for label, callback in VIDEO_MENU_COMMANDS:
        video_menu.add_command(label=label, command=lambda cb=callback: cb(app))

    return video_menu


def _create_heatmap_menu(app) -> tk.Menu:
    heatmap_menu = tk.Menu(app.root, tearoff=0)
    heatmap_menu.add_command(
        label="Heatmap Settings...",
        command=lambda: show_heatmap_settings_window(app),
    )
    return heatmap_menu


def create_menu_bar(app):
    menubar = tk.Menu(app.root)

    file_menu = _create_file_menu(app, menubar)
    menubar.add_cascade(label="File", menu=file_menu)

    video_menu = _create_video_menu(app, menubar)
    menubar.add_cascade(label="Video", menu=video_menu)

    heatmap_menu = _create_heatmap_menu(app)
    menubar.add_cascade(label="Heatmap", menu=heatmap_menu)

    app.background_menu = tk.Menu(menubar, tearoff=0)
    update_background_menu(app)
    menubar.add_cascade(label="Background", menu=app.background_menu)

    app.root.config(menu=menubar)


def update_background_menu(app):
    if not hasattr(app, "background_menu"):
        return

    app.background_menu.delete(0, "end")

    for bg in getattr(app, "bg_files", []):
        app.background_menu.add_command(
            label=bg,
            command=lambda b=bg: app.set_background(b),
        )
