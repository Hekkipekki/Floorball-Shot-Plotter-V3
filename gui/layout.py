# gui/layout.py
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from gui.plot_canvas import setup_plot_canvas
from utils.tooltips import BetterToolTip
from gui.controls import (
    setup_period_controls,
    setup_view_mode_controls,
    setup_stats_filter_controls,
    setup_expected_goals_controls,
    setup_heatmap_settings_group,
    setup_match_management,
    setup_demo_shots_button
)
from gui.shotlog import setup_shotlog_frame


def setup_ui(self):
    self.style = tb.Style()
    self.style.theme_use("flatly")

    # Grid-konfiguration för root
    self.root.grid_columnconfigure(0, minsize=240, weight=0)  # left panel
    self.root.grid_columnconfigure(1, weight=1)              # center panel expands
    self.root.grid_columnconfigure(2, minsize=260, weight=0)  # right panel
    self.root.grid_rowconfigure(0, weight=1)

    # LEFT PANEL
    self.left_panel = tb.Frame(self.root, width=240)
    self.left_panel.grid(row=0, column=0, sticky="nsw", padx=(5, 0))
    self.left_panel.pack_propagate(False)

    # CENTER PANEL
    self.center_panel = tb.Frame(self.root)
    self.center_panel.grid(row=0, column=1, sticky="nsew")

    # PLOT CANVAS
    setup_plot_canvas(self)

    # RIGHT PANEL
    self.right_panel = tb.Frame(self.root, width=260)
    self.right_panel.grid(row=0, column=2, sticky="nse", pady=0)
    self.right_panel.grid_rowconfigure(0, weight=1)

    # SHOT LOG (måste initieras innan stats)
    setup_shotlog_frame(self, self.right_panel, self)

    # LEFT CONTROLS
    setup_period_controls(self, self.left_panel)
    setup_view_mode_controls(self, self.left_panel)
    setup_stats_filter_controls(self, self.left_panel)
    setup_expected_goals_controls(self, self.left_panel)
    setup_heatmap_settings_group(self, self.left_panel)
    setup_match_management(self, self.left_panel)
    setup_demo_shots_button(self, self.left_panel)

    self.update_match_dropdown()
    create_menu_bar(self)

    self.update_stats_filtered()

def create_menu_bar(self):
    menubar = tk.Menu(self.root)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Save CSV", command=self.save_csv)
    file_menu.add_command(label="Load CSV", command=self.load_csv)
    file_menu.add_separator()
    file_menu.add_command(label="Export Image", command=self.export_plot)
    menubar.add_cascade(label="File", menu=file_menu)

    self.background_menu = tk.Menu(menubar, tearoff=0)
    for bg in self.bg_files:
        self.background_menu.add_command(
            label=bg,
            command=lambda b=bg: self.set_background(b) if hasattr(self, "set_background") else print(f"⚠️ set_background not implemented for {b}")
        )
    menubar.add_cascade(label="Background", menu=self.background_menu)

    self.root.config(menu=menubar)


def update_background_menu(self):
    """Uppdatera bakgrundsmenyn dynamiskt."""
    if hasattr(self, "background_menu"):
        self.background_menu.delete(0, "end")
        for bg in self.bg_files:
            self.background_menu.add_command(
                label=bg,
                command=lambda b=bg: self.set_background(b) if hasattr(self, "set_background") else print(f"⚠️ set_background not implemented for {b}")
            )
