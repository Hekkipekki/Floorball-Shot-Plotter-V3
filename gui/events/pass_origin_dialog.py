import tkinter as tk

from gui.events.popup_utils import prepare_popup

GOAL_EVENT_TYPE = "goal"
DIALOG_TITLE = "Mark Pass Origin?"
DIALOG_MESSAGE = "Do you want to place a pass origin point?"
BUTTON_BG = "#223344"
BUTTON_FG = "white"
BUTTON_FONT = ("Arial", 9, "bold")
DIALOG_WIDTH = 320
DIALOG_HEIGHT = 150


def _event_adder(app, event_type: str):
    return app.add_goal_event if event_type == GOAL_EVENT_TYPE else app.add_shot_event


def _set_pending_pass(app, data) -> None:
    app.pending_pass_data = data
    app.expecting_pass_click = True


def _button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        bg=BUTTON_BG,
        fg=BUTTON_FG,
        font=BUTTON_FONT,
        command=command,
    )


def _on_mark_manually(app, popup, pending_data) -> None:
    popup.destroy()
    _set_pending_pass(app, pending_data)


def _on_skip_pass_origin(popup, add_event, x, y, phase, situation, shot_type, passer, shooter) -> None:
    popup.destroy()
    add_event(x, y, phase, situation, shot_type, passer, shooter)


def show_pass_origin_dialog(app, x, y, phase, situation, shot_type, passer, shooter, event_type):
    popup = tk.Toplevel(app.root)
    popup.title(DIALOG_TITLE)
    popup.transient(app.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())
    popup.bind("<Destroy>", lambda _: setattr(app, "popup_open", False))

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    label = tk.Label(
        frame,
        text=DIALOG_MESSAGE,
        wraplength=250,
        justify="center",
        font=BUTTON_FONT,
    )
    label.pack(pady=(0, 15))

    pending_data = (x, y, phase, situation, shot_type, passer, shooter, event_type)
    btn_yes = _button(
        frame,
        "Yes (mark manually)",
        lambda: _on_mark_manually(app, popup, pending_data),
    )
    btn_yes.pack(fill=tk.X, pady=(0, 8))

    add_event = _event_adder(app, event_type)
    btn_no = _button(
        frame,
        "No (skip pass origin)",
        lambda: _on_skip_pass_origin(
            popup,
            add_event,
            x,
            y,
            phase,
            situation,
            shot_type,
            passer,
            shooter,
        ),
    )
    btn_no.pack(fill=tk.X)

    prepare_popup(popup, app, width=DIALOG_WIDTH, height=DIALOG_HEIGHT)
