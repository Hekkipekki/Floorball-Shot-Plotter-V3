from __future__ import annotations

import tkinter as tk
import ttkbootstrap as tb

from gui.panels.left_controls import create_left_panel
from gui.panels.center_plot import create_center_plot
from gui.panels.right_shotlog import create_right_panel
from gui.theme import apply_theme


def setup_ui(app):
    apply_theme(app)

    root = app.root

    main_frame = tb.Frame(root)
    main_frame.pack(fill="both", expand=True)

    # Important: create side panels first, then center last
    app.left_panel = create_left_panel(main_frame, app)
    app.right_panel = create_right_panel(main_frame, app)
    app.center_panel = create_center_plot(main_frame, app)

    create_menu_bar(app)

    app.update_match_dropdown()
    app.update_stats_filtered()


def create_menu_bar(app):
    menubar = tk.Menu(app.root)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Save CSV", command=app.save_csv)
    file_menu.add_command(label="Load CSV", command=app.load_csv)
    file_menu.add_separator()
    file_menu.add_command(label="Export Image", command=app.export_plot)
    menubar.add_cascade(label="File", menu=file_menu)

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