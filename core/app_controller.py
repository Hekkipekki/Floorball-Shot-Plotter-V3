import os
import tkinter as tk
from PIL import Image, ImageTk
import ttkbootstrap as tb

from core.demo import generate_demo_shots
from core.init_state import init_variables
from core.core_stats import CoreLogic

from gui.layout import setup_ui
from gui.events import finalize_event
from gui.backgrounds import init_background_files, set_background
from gui.plot_controller import (
    update_plot,
    apply_sensitivity,
    apply_kde,
    clear_highlight,
    connect_hover_events,
    highlight_point,
    remove_nearest_point,
)

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

from services.event_service import add_shot_event, add_goal_event

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

        self._ensure_new_match()
        self.current_match.set("New Match")

        self.logic = CoreLogic(self)

        init_background_files(self)
        self.set_background = lambda name: set_background(self, name)

        setup_ui(self)
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

    def _ensure_new_match(self):
        if not hasattr(self, "match_logs"):
            self.match_logs = {}

        if "New Match" not in self.match_logs:
            self.match_logs["New Match"] = []

    # ---------------------------------------------------------
    # UI compatibility helpers
    # ---------------------------------------------------------
    def update_match_dropdown(self):
        if not hasattr(self, "match_dropdown"):
            return

        matches = list(self.match_logs.keys())

        if "All" not in matches:
            matches.insert(0, "All")

        self.match_dropdown["values"] = matches

        current = self.current_match.get()
        if current not in matches:
            self.current_match.set("New Match" if "New Match" in matches else matches[0])

    def clear_all_data(self):
        match_name = self.current_match.get()

        if match_name in ("All", "Season"):
            return

        if match_name not in self.match_logs:
            self.match_logs[match_name] = []

        self.match_logs[match_name] = []
        self.log_entries = []
        self.update_log_view_and_stats()

    def generate_demo_shots(self):
        generate_demo_shots(self)

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

    def update_stats_filtered(self):
        self.update_log_view_and_stats()

    def update_stats(self):
        self.logic.update_stats()

    def update_expected_goals(self):
        self.logic.update_expected_goals()

    def get_filtered_entries(self):
        return self.logic.get_filtered_entries()

    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------
    def add_shot_event(self, *args, **kwargs):
        add_shot_event(self, *args, **kwargs)
        self.update_log_view_and_stats()

    def add_goal_event(self, *args, **kwargs):
        add_goal_event(self, *args, **kwargs)
        self.update_log_view_and_stats()

    # ---------------------------------------------------------
    # Match / Data
    # ---------------------------------------------------------
    def prompt_save_match(self):
        prompt_save_match(self)

    def handle_load_match(self):
        self.load_match()

    def handle_load_season(self):
        self.load_season()

    def load_selected_match(self, *_):
        load_selected_match(self)

    def load_match(self):
        load_match_from_file(self)

    def load_season(self):
        load_all_matches(self)

    def delete_current_match(self):
        delete_current_match(self)

    def auto_update_current_match(self):
        auto_update_current_match(self)

    def save_csv(self):
        save_csv_dialog(self)

    def load_csv(self):
        load_csv_dialog(self)