import tkinter as tk

from gui.events.popup_utils import prepare_popup


def _event_adder(app, event_type: str):
    return app.add_goal_event if event_type == "goal" else app.add_shot_event


def show_pass_origin_dialog(app, x, y, phase, situation, shot_type, passer, shooter, event_type):
    popup = tk.Toplevel(app.root)
    popup.title("Mark Pass Origin?")
    popup.transient(app.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())
    popup.bind("<Destroy>", lambda _: setattr(app, "popup_open", False))

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    label = tk.Label(
        frame,
        text="Do you want to place a pass origin point?",
        wraplength=250,
        justify="center",
        font=("Arial", 9, "bold"),
    )
    label.pack(pady=(0, 15))

    btn_yes = tk.Button(
        frame,
        text="Yes (mark manually)",
        bg="#223344",
        fg="white",
        font=("Arial", 9, "bold"),
        command=lambda: [
            popup.destroy(),
            setattr(
                app,
                "pending_pass_data",
                (x, y, phase, situation, shot_type, passer, shooter, event_type),
            ),
            setattr(app, "expecting_pass_click", True),
        ],
    )
    btn_yes.pack(fill=tk.X, pady=(0, 8))

    add_event = _event_adder(app, event_type)

    btn_no = tk.Button(
        frame,
        text="No (skip pass origin)",
        bg="#223344",
        fg="white",
        font=("Arial", 9, "bold"),
        command=lambda: [
            popup.destroy(),
            add_event(x, y, phase, situation, shot_type, passer, shooter),
        ],
    )
    btn_no.pack(fill=tk.X)

    prepare_popup(popup, app, width=320, height=150)
