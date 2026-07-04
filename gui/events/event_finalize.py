def finalize_event(app, x, y, phase, situation, shot_type, passer, shooter, shot_or_goal, popup=None):
    x = int(round(x))
    y = int(round(y))

    if popup:
        popup.destroy()

    if app.view_mode.get() != "Plot":
        print("⛔ Cannot place shots outside of Plot view.")
        return

    unassisted = situation == "Penalty Shot" or shot_type == "Free shot"

    if unassisted:
        if shot_or_goal == "goal":
            app.add_goal_event(x, y, phase, situation, shot_type, passer, shooter)
        else:
            app.add_shot_event(x, y, phase, situation, shot_type, passer, shooter)
        return

    from gui.events.event_dialogs import show_pass_origin_dialog

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
