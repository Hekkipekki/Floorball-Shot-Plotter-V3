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

DEFAULT_MATCH_NAME = "New Match"
READ_ONLY_MATCHES = ("All", "Season")


def ensure_new_match_exists(app):
    if not hasattr(app, "match_logs"):
        app.match_logs = {}
    if DEFAULT_MATCH_NAME not in app.match_logs:
        app.match_logs[DEFAULT_MATCH_NAME] = []


def ensure_current_match_is_valid(app):
    current = app.current_match.get()
    if current not in app.match_logs and current not in READ_ONLY_MATCHES:
        if DEFAULT_MATCH_NAME in app.match_logs:
            app.current_match.set(DEFAULT_MATCH_NAME)
        elif app.match_logs:
            app.current_match.set(next(iter(app.match_logs)))
        else:
            app.match_logs[DEFAULT_MATCH_NAME] = []
            app.current_match.set(DEFAULT_MATCH_NAME)


def _sync_shotlog_match_filter(app) -> None:
    sync = getattr(app, "sync_shotlog_match_filter", None)
    if sync is not None:
        sync()


def _reset_shotlog_match_filter(app) -> None:
    all_var = getattr(app, "shotlog_match_filter_all", None)
    match_vars = getattr(app, "shotlog_match_filter_vars", None)

    if all_var is not None:
        all_var.set(True)
    if match_vars is not None:
        for var in match_vars.values():
            var.set(False)

    _sync_shotlog_match_filter(app)


def _next_new_match_name(app) -> str:
    existing = set(app.match_logs.keys())
    if DEFAULT_MATCH_NAME not in existing or not app.match_logs.get(DEFAULT_MATCH_NAME):
        return DEFAULT_MATCH_NAME

    counter = 2
    while f"{DEFAULT_MATCH_NAME} {counter}" in existing:
        counter += 1
    return f"{DEFAULT_MATCH_NAME} {counter}"


def update_match_dropdown(app):
    if not hasattr(app, "match_dropdown"):
        _sync_shotlog_match_filter(app)
        return

    matches = list(app.match_logs.keys())
    if "All" not in matches:
        matches.insert(0, "All")

    app.match_dropdown["values"] = matches
    ensure_current_match_is_valid(app)
    _sync_shotlog_match_filter(app)


def start_new_match(app):
    name = _next_new_match_name(app)
    app.match_logs[name] = []
    app.log_entries = []
    app.current_match.set(name)
    app.period_selected.set("All")
    app.stats_period.set("All")
    _reset_shotlog_match_filter(app)
    update_match_dropdown(app)
    load_selected_match(app)
    app.refresh_all()


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
        app.current_match.set(DEFAULT_MATCH_NAME)
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
    _reset_shotlog_match_filter(app)
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
