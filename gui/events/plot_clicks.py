PLOT_VIEW_MODE = "Plot"
SHOT_EVENT_TYPE = "shot"
GOAL_EVENT_TYPE = "goal"
LEFT_CLICK_BUTTON = 1
RIGHT_CLICK_BUTTON = 3
PENDING_PASS_DATA_WITH_TYPE_LENGTH = 8


def on_space_key_pressed(app, event):
    app.remove_nearest_point()


def is_plot_click_allowed(app, event):
    if app.view_mode.get() != PLOT_VIEW_MODE:
        print("Cannot place events outside of Plot view mode.")
        return False

    if event.xdata is None or event.ydata is None or app.popup_open:
        return False

    return True


def _pending_pass_data(app):
    if not hasattr(app, "pending_pass_data"):
        return None
    return app.pending_pass_data


def _unpack_pending_pass_data(data):
    if len(data) == PENDING_PASS_DATA_WITH_TYPE_LENGTH:
        return data

    main_x, main_y, phase, situation, shot_type, passer, shooter = data
    return main_x, main_y, phase, situation, shot_type, passer, shooter, SHOT_EVENT_TYPE


def _event_coordinates(event):
    return int(round(event.xdata)), int(round(event.ydata))


def _event_adder(app, event_type):
    return app.add_goal_event if event_type == GOAL_EVENT_TYPE else app.add_shot_event


def _clear_pending_pass_data(app) -> None:
    if hasattr(app, "pending_pass_data"):
        del app.pending_pass_data


def _add_pending_pass_event(app, event):
    app.expecting_pass_click = False

    data = _pending_pass_data(app)
    if data is None:
        return

    main_x, main_y, phase, situation, shot_type, passer, shooter, event_type = _unpack_pending_pass_data(data)
    pass_x, pass_y = _event_coordinates(event)
    add_event = _event_adder(app, event_type)
    add_event(
        main_x,
        main_y,
        phase,
        situation,
        shot_type,
        passer,
        shooter,
        pass_x=pass_x,
        pass_y=pass_y,
    )
    _clear_pending_pass_data(app)


def _show_event_dialog(app, event, shot_or_goal):
    from gui.events.event_dialogs import show_phase_dialog

    show_phase_dialog(app, event.xdata, event.ydata, shot_or_goal=shot_or_goal)


def onclick(app, event):
    if not is_plot_click_allowed(app, event):
        return

    if getattr(app, "expecting_pass_click", False):
        _add_pending_pass_event(app, event)
        return

    if event.button == LEFT_CLICK_BUTTON:
        _show_event_dialog(app, event, shot_or_goal=SHOT_EVENT_TYPE)
    elif event.button == RIGHT_CLICK_BUTTON:
        _show_event_dialog(app, event, shot_or_goal=GOAL_EVENT_TYPE)
