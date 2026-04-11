import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb

from core.demo import generate_demo_shots as demo_fill
from core.init_state import init_variables
from core.core_stats import CoreLogic

from gui.layout import setup_ui
from gui.events import finalize_event
from gui.backgrounds import init_background_files, set_background
from gui.plot_controller import (
    load_image,
    update_plot,
    apply_sensitivity,
    apply_kde,
    clear_highlight,
    connect_hover_events,
    highlight_point,
    remove_nearest_point,
)
from gui.shotlog import update_treeview

from data.match_store import (
    prompt_save_match,
    load_selected_match,
    load_match_from_file,
    load_all_matches,
    delete_current_match,
    auto_update_current_match,
    save_csv_dialog,
    load_csv_dialog,
)

from paths import get_project_root
from utils.helpers import get_resource_path, export_figure_as_image
from utils.tooltips import add_tooltips


APP_TITLE = "Floorball Shot Plotter v3.0 - By Daniel Norberg"
GAMES_DIR = "Games"


class FloorballShotPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)

        self._configure_window()
        self._configure_paths()
        self._load_icons()

        self.popup_open = False
        self.video_overlay = None

        init_variables(self)

        self.ensure_new_match_exists()
        self.current_match.set("New Match")

        self.logic = CoreLogic(self)

        init_background_files(self)
        self.set_background = lambda name: set_background(self, name)

        setup_ui(self)

        load_image(self)
        self.update_plot()

        self._bind_events()
        add_tooltips(self)

        self.finalize_event = lambda *args, **kwargs: finalize_event(self, *args, **kwargs)

    # ---------------------------------------------------------
    # Bootstrap
    # ---------------------------------------------------------
    def _configure_window(self):
        try:
            self.root.state("zoomed")
        except Exception:
            w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
            self.root.geometry(f"{w}x{h}+0+0")

        self.root.bind("<Escape>", lambda e: self.root.state("normal"))

    def _configure_paths(self):
        self.project_root = get_project_root()
        os.makedirs(os.path.join(self.project_root, GAMES_DIR), exist_ok=True)

    def _load_icons(self):
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

    def _bind_events(self):
        self.root.bind_all("<space>", lambda e: remove_nearest_point(self, e))
        self.root.bind_all("<Key-space>", lambda e: remove_nearest_point(self, e))
        connect_hover_events(self)

    # ---------------------------------------------------------
    # Match safety
    # ---------------------------------------------------------
    def ensure_new_match_exists(self):
        if not hasattr(self, "match_logs"):
            self.match_logs = {}
        if "New Match" not in self.match_logs:
            self.match_logs["New Match"] = []

    def ensure_current_match_is_valid(self):
        current = self.current_match.get()
        if current not in self.match_logs and current not in ("All", "Season"):
            if "New Match" in self.match_logs:
                self.current_match.set("New Match")
            elif self.match_logs:
                self.current_match.set(next(iter(self.match_logs)))
            else:
                self.match_logs["New Match"] = []
                self.current_match.set("New Match")

    def update_match_dropdown(self):
        if not hasattr(self, "match_dropdown"):
            return

        matches = list(self.match_logs.keys())
        if "All" not in matches:
            matches.insert(0, "All")

        self.match_dropdown["values"] = matches
        self.ensure_current_match_is_valid()

    # ---------------------------------------------------------
    # Plot
    # ---------------------------------------------------------
    def update_plot(self):
        update_plot(self)

    def apply_sensitivity(self, from_slider=False):
        apply_sensitivity(self, from_slider)

    def apply_kde(self, from_slider=False):
        apply_kde(self, from_slider)

    def highlight_point(self, index):
        highlight_point(self, index)

    def clear_highlight(self):
        clear_highlight(self)

    def remove_nearest_point(self, event=None):
        remove_nearest_point(self, event)

    def export_plot(self):
        export_figure_as_image(self, self.figure)

    # ---------------------------------------------------------
    # Stats / Log
    # ---------------------------------------------------------
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

    def get_filtered_entries(self):
        return self.logic.get_filtered_entries()

    # ---------------------------------------------------------
    # Events
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
        current = self.current_match.get()
        if current in self.match_logs:
            self.match_logs[current] = []
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
    # Match / Data
    # ---------------------------------------------------------
    def save_csv(self):
        save_csv_dialog(self)

    def load_csv(self):
        load_csv_dialog(self)
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