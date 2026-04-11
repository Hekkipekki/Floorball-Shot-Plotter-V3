def on_space_key_pressed(app, event):
    app.remove_nearest_point()


def is_plot_click_allowed(app, event):
    if app.view_mode.get() != "Plot":
        print("⛔ Cannot place shots/goals outside of Plot view mode.")
        return False

    if event.xdata is None or event.ydata is None or app.popup_open:
        return False

    return True


def onclick(self, event):
    if not is_plot_click_allowed(self, event):
        return

    if getattr(self, "expecting_pass_click", False):
        self.expecting_pass_click = False
        if hasattr(self, "pending_pass_data"):
            main_x, main_y, phase, situation, shot_type, passer, shooter = self.pending_pass_data
            pass_x = int(round(event.xdata))
            pass_y = int(round(event.ydata))
            self.add_shot_event(
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
            del self.pending_pass_data
        return

    from gui.events.event_dialogs import show_phase_dialog

    if event.button == 1:
        show_phase_dialog(self, event.xdata, event.ydata, shot_or_goal="shot")
    elif event.button == 3:
        show_phase_dialog(self, event.xdata, event.ydata, shot_or_goal="goal")