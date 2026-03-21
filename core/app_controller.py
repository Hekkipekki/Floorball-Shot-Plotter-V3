import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb  # kept because other modules might rely on ttkbootstrap styles

from core.init_state import init_variables
from core.core_stats import CoreLogic
from core.demo import generate_demo_shots as demo_fill

from gui.layout import setup_ui
from gui.events import finalize_event
from gui.plot_controller import (
    load_image,
    update_plot,
    apply_sensitivity,
    apply_kde,
    highlight_point,
    clear_highlight,
    connect_hover_events,
    remove_nearest_point,
)
from gui.shotlog import update_treeview
from gui.backgrounds import init_background_files, set_background

from utils.helpers import export_figure_as_image, get_resource_path
from utils.tooltips import add_tooltips, update_preset_tooltip
from paths import get_project_root

from data.match_store import (
    prompt_save_match,
    load_match_from_file,
    load_selected_match,
    auto_update_current_match,
    delete_current_match,
    save_csv_dialog,
    load_csv_dialog,
    load_all_matches,
)

APP_TITLE = "Floorball Shot Plotter v3.0 - By Daniel Norberg"
RESOURCES_DIR = "Resources"
GAMES_DIR = "Games"
FIRST_RUN_FILE = "first_run.txt"


class FloorballShotPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)

        # 💝 Fullskärmsläge
        try:
            self.root.state("zoomed")
        except Exception:
            w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")
        self.root.bind("<Escape>", lambda e: self.root.state("normal"))

        # 🗂️ Paths
        self.project_root = get_project_root()
        os.makedirs(os.path.join(self.project_root, GAMES_DIR), exist_ok=True)

        # 🧩 Ikoner
        icon_path = get_resource_path("Resources", "Icons", "Icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        trash_path = get_resource_path("Resources", "Icons", "trash.png")
        try:
            img = Image.open(trash_path).convert("RGBA")
            self.trash_icon = ImageTk.PhotoImage(img)
        except Exception:
            self.trash_icon = None

        # Overlay/video state
        self.popup_open = False
        self.video_overlay = None

        # 🔧 Init core state
        init_variables(self)

        # Defensive: always keep a valid default match
        self.ensure_new_match_exists()
        self.current_match.set("New Match")

        # Init logic + background files
        self.logic = CoreLogic(self)
        init_background_files(self)
        self.set_background = lambda b: set_background(self, b)

        print(f"DEBUG: Initial match_logs keys = {list(self.match_logs.keys())}")
        print(f"DEBUG: Current match set to = {self.current_match.get()}")

        # Build UI
        setup_ui(self)

        # ✅ Remove nearest (Space)
        self.root.bind_all("<space>", lambda e: remove_nearest_point(self, e))
        self.root.bind_all("<Key-space>", lambda e: remove_nearest_point(self, e))

        # Connect hover events in canvas
        connect_hover_events(self)

        # Tooltips, defaults, preset tooltip
        add_tooltips(self)
        self.load_defaults()
        update_preset_tooltip(self)

        # 📌 Event hook
        self.finalize_event = lambda *args, **kwargs: finalize_event(self, *args, **kwargs)

        # First-run info
        self.check_first_run()

    # ---------------------------------------------------------
    # Safety helpers
    # ---------------------------------------------------------
    def ensure_new_match_exists(self):
        """Guarantee that 'New Match' always exists in match_logs."""
        if not hasattr(self, "match_logs") or self.match_logs is None:
            self.match_logs = {}
        if "New Match" not in self.match_logs:
            self.match_logs["New Match"] = []

    def ensure_current_match_is_valid(self):
        """
        Ensure current_match points to an existing key.
        Prefer 'New Match' as the safe fallback.
        """
        self.ensure_new_match_exists()
        cur = self.current_match.get() if hasattr(self, "current_match") else None
        if not cur or cur not in self.match_logs:
            self.current_match.set("New Match")

    # ---------------------------------------------------------
    # Init / UI defaults
    # ---------------------------------------------------------
    def check_first_run(self):
        first_run_path = os.path.join(self.project_root, FIRST_RUN_FILE)
        if not os.path.exists(first_run_path):
            messagebox.showinfo(
                "First Run",
                "The first time you run the program it may take longer as resources are extracted.",
            )
            try:
                with open(first_run_path, "w", encoding="utf-8") as f:
                    f.write("This file indicates first run")
            except Exception:
                pass

    def load_defaults(self):
        load_image(self)
        update_plot(self)

    def update_match_dropdown(self):
        """
        Called after you add/remove matches.
        Ensures dropdown contains keys and selection is valid.
        """
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()

        if hasattr(self, "match_dropdown"):
            keys = list(self.match_logs.keys()) if self.match_logs else ["New Match"]
            self.match_dropdown["values"] = keys
            if self.current_match.get() not in keys:
                self.current_match.set("New Match")

    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------
    def update_plot(self):
        update_plot(self)

    def apply_sensitivity(self, from_slider=False):
        apply_sensitivity(self, from_slider=from_slider)

    def apply_kde(self, from_slider=False):
        apply_kde(self, from_slider=from_slider)

    def on_preset_changed(self):
        self.logic.apply_heatmap_preset()
        self.logic.update_preset_description()
        update_preset_tooltip(self)

    def highlight_point(self, index):
        highlight_point(self, index)

    def clear_highlight(self):
        clear_highlight(self)

    def export_plot(self):
        export_figure_as_image(self, self.figure)

    # ---------------------------------------------------------
    # Logg och Statistik
    # ---------------------------------------------------------
    def get_filtered_entries(self):
        return self.logic.get_filtered_entries()

    def update_log_view_and_stats(self):
        self.logic.update_log_view_and_stats()

    def update_shot_log_treeview(self):
        update_treeview(self.shotlog_tree, self.log_entries)

    def update_period_button_styles(self):
        selected = self.period_selected.get()
        for period, btn in self.period_buttons.items():
            style = "primary" if selected == period else "secondary"
            btn.config(bootstyle=style)

    def set_period_filter(self, period):
        self.period_selected.set(period)
        self.update_period_button_styles()
        self.logic.update_log_view_and_stats()

    def update_stats(self, entries=None):
        self.logic.update_stats(entries)

    def update_stats_filtered(self):
        self.logic.update_log_view_and_stats()

    def update_expected_goals(self):
        self.logic.update_expected_goals()

    # ---------------------------------------------------------
    # Händelser
    # ---------------------------------------------------------
    def add_shot_event(self, x, y, phase, situation, shot_type, passer, shooter, period=None, pass_x=None, pass_y=None):
        self.logic.add_shot_event(x, y, phase, situation, shot_type, passer, shooter, period, pass_x, pass_y)
        self.log_entries = self.logic.get_filtered_entries()
        self.update_log_view_and_stats()

    def add_goal_event(self, x, y, phase, situation, shot_type, passer, shooter, period=None, pass_x=None, pass_y=None):
        self.logic.add_goal_event(x, y, phase, situation, shot_type, passer, shooter, period, pass_x, pass_y)
        self.log_entries = self.logic.get_filtered_entries()
        self.update_log_view_and_stats()

    def clear_all_data(self):
        self.log_entries.clear()
        self.update_log_view_and_stats()

    def new_project(self):
        if messagebox.askyesno("New Project", "Start a new project? This will clear all data."):
            self.clear_all_data()
            self.ensure_new_match_exists()
            self.current_match.set("New Match")
            self.update_match_dropdown()

    def generate_demo_shots(self):
        demo_fill(self)

    # ---------------------------------------------------------
    # Matchhantering (wrappers)
    # ---------------------------------------------------------
    def save_csv(self):
        save_csv_dialog(self)

    def load_csv(self):
        load_csv_dialog(self)
        # keep selection safe after load
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()
        self.update_match_dropdown()

    def prompt_save_match(self):
        prompt_save_match(self)
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()
        self.update_match_dropdown()

    def load_selected_match(self, *_):
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()
        load_selected_match(self)
        self.update_match_dropdown()

    def handle_load_season(self):
        load_all_matches(self)
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()
        self.update_match_dropdown()

    def handle_load_match(self):
        load_match_from_file(self)
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()
        self.update_match_dropdown()

    def auto_update_current_match(self):
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()
        auto_update_current_match(self)

    def delete_current_match(self):
        delete_current_match(self)
        self.ensure_new_match_exists()
        self.ensure_current_match_is_valid()
        self.update_match_dropdown()