import tkinter as tk

from gui.events.popup_utils import prepare_popup
from gui.events.event_finalize import finalize_event


def _create_base_popup(app, title, on_destroy=None):
    popup = tk.Toplevel(app.root)
    popup.title(title)
    popup.transient(app.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())

    if on_destroy is not None:
        popup.bind("<Destroy>", lambda _: on_destroy())

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    desc_label = tk.Label(
        frame,
        text="",
        wraplength=250,
        justify="center",
        anchor="center",
    )
    desc_label.pack_forget()

    return popup, frame, desc_label


def show_option_dialog(
    app,
    title,
    options,
    on_select,
    width,
    height,
    on_destroy=None,
):
    popup, frame, desc_label = _create_base_popup(app, title, on_destroy=on_destroy)

    for label, description in options.items():
        btn = tk.Button(
            frame,
            text=label,
            bg="#223344",
            fg="white",
            relief=tk.RAISED,
            padx=10,
            pady=5,
            anchor="center",
            justify="center",
            font=("Arial", 9, "bold"),
            command=lambda value=label: [popup.destroy(), on_select(value)],
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda e: desc_label.config(text=""))

    desc_label.pack(fill=tk.BOTH, expand=True, pady=(10, 5))

    cancel = tk.Button(frame, text="Cancel", command=popup.destroy)
    cancel.pack(fill=tk.X, pady=(0, 5))

    prepare_popup(popup, app, width=width, height=height)


def show_phase_dialog(self, x, y, shot_or_goal):
    if self.popup_open:
        return

    self.popup_open = True

    phases = {
        "Full Court press": "Trying to activate from the normal entry defense, up to a full court press.",
        "Zone entry defense": "The team is playing the normal defense system, trying to prevent the opponent from playing a zone entry with quality.",
        "Zone Defense": "You are trying to defend after the opponent has settled in playing zone offense.",
        "Zone Exit": "The opponent activates counter-press after you have won the ball in your own zone.",
        "Counter on counter": "When a team counters after having won the ball from the opponent's counter-attack.",
        "Uncontrolled": "When a situation cannot be placed under any other game situation.",
    }

    show_option_dialog(
        self,
        title="Select Phase",
        options=phases,
        on_select=lambda phase: show_situation_dialog(self, x, y, phase, shot_or_goal),
        width=265,
        height=350,
        on_destroy=lambda: setattr(self, "popup_open", False),
    )


def show_situation_dialog(self, x, y, phase, shot_or_goal):
    situations = {
        "Breakaway": "Attacker breaks through alone on the goalkeeper.",
        "2v0": "Two attackers against the goalkeeper without defenders.",
        "2v1": "Two attackers versus one defender.",
        "3v1": "Three attackers versus one defender.",
        "3v2": "Three attackers versus two defenders.",
        "Rebound": "Shot opportunity following a saved or blocked shot.",
        "Penalty Shot": "Awarded direct shot from penalty mark.",
        "Free shot": "No pressure or game system affects this situation.",
    }

    show_option_dialog(
        self,
        title="Select Situation",
        options=situations,
        on_select=lambda situation: show_shot_type_dialog(self, x, y, phase, situation, shot_or_goal),
        width=265,
        height=370,
    )


def show_shot_type_dialog(self, x, y, phase, situation, shot_or_goal):
    shot_types = {
        "One-timer": "A direct shot taken immediately after receiving the ball.",
        "Controlled shot": "A composed, aimed shot with time and balance.",
        "Own Goal": "Shot directed by defending team into their own net.",
        "Deke": "A deceptive move to fake out the goalie before shooting.",
        "Deflection": "A shot redirected by a player’s stick or body after an initial shot or pass.",
        "Penalty Shot": "Awarded direct shot from penalty mark.",
        "Free shot": "Direct Shot, no passes.",
    }

    show_option_dialog(
        self,
        title="Select Shot Type",
        options=shot_types,
        on_select=lambda shot_type: show_shooter_hand_dialog(
            self, x, y, phase, situation, shot_type, shot_or_goal
        ),
        width=265,
        height=320,
    )


def show_shooter_hand_dialog(self, x, y, phase, situation, shot_type, shot_or_goal):
    hands = {
        "Left": "Shooter holds the stick on the left side.",
        "Right": "Shooter holds the stick on the right side.",
    }

    def handle_selection(shooter_hand):
        unassisted = situation in ("Free shot", "Penalty Shot") or shot_type in ("Free shot", "Penalty Shot")
        if unassisted:
            finalize_event(self, x, y, phase, situation, shot_type, "", shooter_hand, shot_or_goal)
        else:
            show_passer_hand_dialog(self, x, y, phase, situation, shot_type, shooter_hand, shot_or_goal)

    show_option_dialog(
        self,
        title="Shooter Stick Hand",
        options=hands,
        on_select=handle_selection,
        width=265,
        height=150,
    )


def show_passer_hand_dialog(self, x, y, phase, situation, shot_type, shooter, shot_or_goal):
    hands = {
        "Left": "Passer holds the stick on the left side.",
        "Right": "Passer holds the stick on the right side.",
    }

    show_option_dialog(
        self,
        title="Passer Stick Hand",
        options=hands,
        on_select=lambda passer_hand: finalize_event(
            self, x, y, phase, situation, shot_type, passer_hand, shooter, shot_or_goal
        ),
        width=265,
        height=150,
    )


def show_pass_origin_dialog(self, x, y, phase, situation, shot_type, passer, shooter):
    popup = tk.Toplevel(self.root)
    popup.title("Mark Pass Origin?")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())
    popup.bind("<Destroy>", lambda _: setattr(self, "popup_open", False))

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
        bg="#27ae60",
        fg="white",
        font=("Arial", 8, "bold"),
        command=lambda: [
            popup.destroy(),
            setattr(self, "pending_pass_data", (x, y, phase, situation, shot_type, passer, shooter)),
            setattr(self, "expecting_pass_click", True),
        ],
    )
    btn_yes.pack(fill=tk.X, pady=(0, 8))

    btn_no = tk.Button(
        frame,
        text="No (skip pass origin)",
        bg="#c0392b",
        fg="white",
        font=("Arial", 10, "bold"),
        command=lambda: [
            popup.destroy(),
            self.add_shot_event(x, y, phase, situation, shot_type, passer, shooter),
        ],
    )
    btn_no.pack(fill=tk.X)

    prepare_popup(popup, self, width=300, height=120)