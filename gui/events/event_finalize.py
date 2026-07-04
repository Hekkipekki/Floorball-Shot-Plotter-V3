PLOT_VIEW_MODE = "Plot"
GOAL_EVENT_TYPE = "goal"
UNASSISTED_SITUATIONS = ("Penalty Shot",)
UNASSISTED_SHOT_TYPES = ("Free shot",)


def _rounded_coordinates(x, y):
    return int(round(x)), int(round(y))


def _is_plot_view(app) -> bool:
    return app.view_mode.get() == PLOT_VIEW_MODE


def _is_unassisted_event(situation, shot_type) -> bool:
    return situation in UNASSISTED_SITUATIONS or shot_type in UNASSISTED_SHOT_TYPES


def _add_unassisted_event(app, x, y, phase, situation, shot_type, passer, shooter, event_type) -> None:
    add_event = app.add_goal_event if event_type == GOAL_EVENT_TYPE else app.add_shot_event
    add_event(x, y, phase, situation, shot_type, passer, shooter)


def finalize_event(app, x, y, phase, situation, shot_type, passer, shooter, shot_or_goal, popup=None):
    x, y = _rounded_coordinates(x, y)

    if popup:
        popup.destroy()

    if not _is_plot_view(app):
        print("⛔ Cannot place shots outside of Plot view.")
        return

    if _is_unassisted_event(situation, shot_type):
        _add_unassisted_event(app, x, y, phase, situation, shot_type, passer, shooter, shot_or_goal)
        return

    from gui.events.pass_origin_dialog import show_pass_origin_dialog

    show_pass_origin_dialog(
        app,
        x,
        y,
        phase,
        situation,
        shot_type,
        passer,
        shooter,
        shot_or_goal,
    )
