from __future__ import annotations

from gui.shotlog_view import update_treeview


def refresh_all(app):
    """
    Single unified refresh pipeline.
    Controller owns visible refresh behavior.
    """
    entries = app.logic.get_filtered_entries()
    app.log_entries = entries

    update_treeview(app.shotlog_tree, app.log_entries)

    stats_entries = app.logic.get_filtered_entries_by_period(
        app.stats_period.get()
    )
    app.logic.update_stats(stats_entries)
    app.logic.update_expected_goals()

    app.update_plot()


def update_log_view_and_stats(app):
    refresh_all(app)


def update_shot_log_treeview(app):
    update_treeview(app.shotlog_tree, app.log_entries)


def update_period_button_styles(app):
    selected = app.period_selected.get()
    for period, btn in app.period_buttons.items():
        style = "primary" if selected == period else "secondary"
        btn.config(bootstyle=style)


def set_period_filter(app, period):
    app.period_selected.set(period)
    update_period_button_styles(app)
    refresh_all(app)