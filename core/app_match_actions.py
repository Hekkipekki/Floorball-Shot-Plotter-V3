from __future__ import annotations

from tkinter import messagebox

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


def ensure_new_match_exists(app):
    if not hasattr(app, "match_logs"):
        app.match_logs = {}
    if "New Match" not in app.match_logs:
        app.match_logs["New Match"] = []


def ensure_current_match_is_valid(app):
    current = app.current_match.get()
    if current not in app.match_logs and current not in ("All", "Season"):
        if "New Match" in app.match_logs:
            app.current_match.set("New Match")
        elif app.match_logs:
            app.current_match.set(next(iter(app.match_logs)))
        else:
            app.match_logs["New Match"] = []
            app.current_match.set("New Match")


def update_match_dropdown(app):
    if not hasattr(app, "match_dropdown"):
        return

    matches = list(app.match_logs.keys())
    if "All" not in matches:
        matches.insert(0, "All")

    app.match_dropdown["values"] = matches
    ensure_current_match_is_valid(app)


def clear_all_data(app):
    app.log_entries.clear()
    current = app.current_match.get()
    if current in app.match_logs:
        app.match_logs[current] = []
    app.refresh_all()


def new_project(app):
    if messagebox.askyesno("New Project", "Start a new project? This will clear all data."):
        clear_all_data(app)
        ensure_new_match_exists(app)
        app.current_match.set("New Match")
        update_match_dropdown(app)


def save_csv(app):
    save_csv_dialog(app)


def load_csv(app):
    load_csv_dialog(app)
    ensure_new_match_exists(app)
    ensure_current_match_is_valid(app)
    update_match_dropdown(app)
    load_selected_match(app)
    app.refresh_all()


def save_match(app):
    prompt_save_match(app)
    ensure_new_match_exists(app)
    ensure_current_match_is_valid(app)
    update_match_dropdown(app)
    load_selected_match(app)
    app.refresh_all()


def select_current_match(app, *_):
    ensure_new_match_exists(app)
    ensure_current_match_is_valid(app)
    load_selected_match(app)
    update_match_dropdown(app)
    app.refresh_all()


def handle_load_season(app):
    load_all_matches(app)
    ensure_new_match_exists(app)
    ensure_current_match_is_valid(app)
    update_match_dropdown(app)
    load_selected_match(app)
    app.refresh_all()


def handle_load_match(app):
    load_match_from_file(app)
    ensure_new_match_exists(app)
    ensure_current_match_is_valid(app)
    update_match_dropdown(app)
    load_selected_match(app)
    app.refresh_all()


def auto_save_current_match(app):
    ensure_new_match_exists(app)
    ensure_current_match_is_valid(app)
    auto_update_current_match(app)


def delete_selected_match(app):
    delete_current_match(app)
    ensure_new_match_exists(app)
    ensure_current_match_is_valid(app)
    update_match_dropdown(app)
    load_selected_match(app)
    app.refresh_all()