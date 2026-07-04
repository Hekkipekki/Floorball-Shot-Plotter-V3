def on_space_key_pressed(app, event):
    app.remove_nearest_point()


def is_plot_click_allowed(app, event):
    if app.view_mode.get() != "Plot":
        print("Cannot place events outside of Plot view mode.")
        return False

    if event.xdata is None or event.ydata is None or app.popup_open:
        return False

    return True


def _add_pending_pass_event(app, event):
    app.expecting_pass_click = False

    if not hasattr(app, "pending_pass_data"):
        return

    data = app.pending_pass_data
    if len(data) == 8:
        main_x, main_y, phase, situation, shot_type, passer, shooter, event_type = data
    else:
        main_x, main_y, phase, situation, shot_type, passer, shooter = data
        event_type = "shot"

    pass_x = int(round(event.xdata))
    pass_y = int(round(event.ydata))
    add_event = app.add_goal_event if event_type == "goal" else app.add_shot_event
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
    del app.pending_pass_data


def onclick(app, event):
    if not is_plot_click_allowed(app, event):
        return

    if getattr(app, "expecting_pass_click", False):
        _add_pending_pass_event(app, event)
        return

    from gui.events.event_dialogs import show_phase_dialog

    if event.button == 1:
        show_phase_dialog(app, event.xdata, event.ydata, shot_or_goal="shot")
    elif event.button == 3:
        show_phase_dialog(app, event.xdata, event.ydata, shot_or_goal="goal")
