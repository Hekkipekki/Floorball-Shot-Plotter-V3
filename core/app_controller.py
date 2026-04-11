import tkinter as tk

import ttkbootstrap as tb

from core.app_bootstrap import (
    bind_events,
    configure_paths,
    configure_window,
    load_icons,
)
from core.app_match_actions import (
    auto_save_current_match,
    clear_all_data,
    delete_selected_match,
    ensure_current_match_is_valid,
    ensure_new_match_exists,
    handle_load_match,
    handle_load_season,
    load_csv,
    new_project,
    save_csv,
    save_match,
    select_current_match,
    update_match_dropdown,
)
from core.app_refresh import (
    refresh_all,
    set_period_filter,
    update_log_view_and_stats,
    update_period_button_styles,
    update_shot_log_treeview,
)
from core.core_stats import CoreLogic
from core.demo import generate_demo_shots as demo_fill
from core.init_state import init_variables
from gui.backgrounds import init_background_files, set_background
from gui.events import finalize_event
from gui.layout import setup_ui
from gui.plot_background import load_image
from gui.plot_rendering import update_plot, apply_sensitivity, apply_kde
from gui.plot_interactions import (
    clear_highlight,
    highlight_point,
    remove_nearest_point,
)
from gui.shotlog_interactions import update_entry_in_all_places
from utils.export import export_figure_as_image
from utils.tooltips import add_tooltips


APP_TITLE = "Floorball Shot Plotter v3.0 - By Daniel Norberg"


class FloorballShotPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)

        configure_window(self)
        configure_paths(self)
        load_icons(self)

        self.popup_open = False
        self.video_overlay = None

        init_variables(self)

        ensure_new_match_exists(self)
        self.current_match.set("New Match")

        self.logic = CoreLogic(self)

        init_background_files(self)
        self.set_background = lambda name: set_background(self, name)

        setup_ui(self)

        self._shotlog_update_entry = lambda visible_index, updated_entry: update_entry_in_all_places(
            self, visible_index, updated_entry
        )

        load_image(self)
        self.update_plot()

        bind_events(self)
        add_tooltips(self)

        self.finalize_event = lambda *args, **kwargs: finalize_event(self, *args, **kwargs)

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

    def on_preset_changed(self):
        self.logic.apply_heatmap_preset()
        self.logic.update_preset_description()

    # ---------------------------------------------------------
    # Refresh / Stats / Log
    # ---------------------------------------------------------
    def refresh_all(self):
        refresh_all(self)

    def update_log_view_and_stats(self):
        update_log_view_and_stats(self)

    def update_shot_log_treeview(self):
        update_shot_log_treeview(self)

    def update_period_button_styles(self):
        update_period_button_styles(self)

    def set_period_filter(self, period):
        set_period_filter(self, period)

    def update_stats(self, entries=None):
        self.logic.update_stats(entries)

    def update_stats_filtered(self):
        self.refresh_all()

    def update_expected_goals(self):
        self.logic.update_expected_goals()

    def get_filtered_entries(self):
        return self.logic.get_filtered_entries()

    # ---------------------------------------------------------
    # Match safety
    # ---------------------------------------------------------
    def ensure_new_match_exists(self):
        ensure_new_match_exists(self)

    def ensure_current_match_is_valid(self):
        ensure_current_match_is_valid(self)

    def update_match_dropdown(self):
        update_match_dropdown(self)

    # ---------------------------------------------------------
    # Events
    # ---------------------------------------------------------
    def add_shot_event(
        self,
        x,
        y,
        phase,
        situation,
        shot_type,
        passer,
        shooter,
        period=None,
        pass_x=None,
        pass_y=None,
    ):
        self.logic.add_shot_event(x, y, phase, situation, shot_type, passer, shooter, period, pass_x, pass_y)
        self.refresh_all()

    def add_goal_event(
        self,
        x,
        y,
        phase,
        situation,
        shot_type,
        passer,
        shooter,
        period=None,
        pass_x=None,
        pass_y=None,
    ):
        self.logic.add_goal_event(x, y, phase, situation, shot_type, passer, shooter, period, pass_x, pass_y)
        self.refresh_all()

    def clear_all_data(self):
        clear_all_data(self)

    def new_project(self):
        new_project(self)

    def generate_demo_shots(self):
        demo_fill(self)

    # ---------------------------------------------------------
    # Match / Data
    # ---------------------------------------------------------
    def save_csv(self):
        save_csv(self)

    def load_csv(self):
        load_csv(self)

    def prompt_save_match(self):
        save_match(self)

    def load_selected_match(self, *_):
        select_current_match(self, *_)

    def handle_load_season(self):
        handle_load_season(self)

    def handle_load_match(self):
        handle_load_match(self)

    def auto_update_current_match(self):
        auto_save_current_match(self)

    def delete_current_match(self):
        delete_selected_match(self)