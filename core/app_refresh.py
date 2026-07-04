from __future__ import annotations

from gui.shotlog_view import update_treeview

SELECTED_PERIOD_STYLE = "primary"
UNSELECTED_PERIOD_STYLE = "secondary"


def _refresh_visible_entries(app):
    entries = app.logic.get_filtered_entries()
    app.log_entries = entries
    update_treeview(app.shotlog_tree, app.log_entries)


def _refresh_stats(app):
    stats_entries = app.logic.get_filtered_entries_by_period(
        app.stats_period.get()
    )
    app.logic.update_stats(stats_entries)
    app.logic.update_expected_goals()


def refresh_all(app):
    """
    Single unified refresh pipeline.
    Controller owns visible refresh behavior.
    """
    _refresh_visible_entries(app)
    _refresh_stats(app)
    app.update_plot()


def update_log_view_and_stats(app):
    refresh_all(app)


def update_shot_log_treeview(app):
    update_treeview(app.shotlog_tree, app.log_entries)


def _period_button_style(selected, period):
    return SELECTED_PERIOD_STYLE if selected == period else UNSELECTED_PERIOD_STYLE


def update_period_button_styles(app):
    selected = app.period_selected.get()
    for period, btn in app.period_buttons.items():
        btn.config(bootstyle=_period_button_style(selected, period))


def set_period_filter(app, period):
    app.period_selected.set(period)
    update_period_button_styles(app)
    refresh_all(app)
