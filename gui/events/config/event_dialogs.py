import tkinter as tk

from gui.events.popup_utils import prepare_popup
from gui.events.event_finalize import finalize_event

from gui.events.config.dialog_config import (
    PHASE_OPTIONS,
    PHASE_DIALOG_SIZE,
    SITUATION_OPTIONS,
    SITUATION_DIALOG_SIZE,
    SHOT_TYPE_OPTIONS,
    SHOT_TYPE_DIALOG_SIZE,
    HAND_OPTIONS,
    HAND_DIALOG_SIZE,
    PASS_ORIGIN_DIALOG_SIZE,
)

from gui.events.config.dialog_style import (
    DIALOG_BUTTON_STYLE,
    DIALOG_LABEL_STYLE,
    DIALOG_PADDING,
    DIALOG_DESC_PADDING,
)


# --- Base builder ---

def show_option_dialog(app, title, options, on_select, size, on_destroy=None):
    popup = tk.Toplevel(app.root)
    popup.title(title)
    popup.transient(app.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())

    if on_destroy:
        popup.bind("<Destroy>", lambda _: on_destroy())

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, **DIALOG_PADDING)

    desc_label = tk.Label(frame, text="", **DIALOG_LABEL_STYLE)
    desc_label.pack_forget()

    for label, description in options.items():
        btn = tk.Button(
            frame,
            text=label,
            command=lambda v=label: [popup.destroy(), on_select(v)],
            **DIALOG_BUTTON_STYLE,
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda e: desc_label.config(text=""))

    desc_label.pack(fill=tk.BOTH, expand=True, pady=DIALOG_DESC_PADDING)

    tk.Button(frame, text="Cancel", command=popup.destroy).pack(fill=tk.X, pady=(0, 5))

    prepare_popup(popup, app, width=size[0], height=size[1])


# --- Dialog flow ---

def show_phase_dialog(self, x, y, shot_or_goal):
    if self.popup_open:
        return

    self.popup_open = True

    show_option_dialog(
        self,
        "Select Phase",
        PHASE_OPTIONS,
        lambda phase: show_situation_dialog(self, x, y, phase, shot_or_goal),
        PHASE_DIALOG_SIZE,
        on_destroy=lambda: setattr(self, "popup_open", False),
    )


def show_situation_dialog(self, x, y, phase, shot_or_goal):
    show_option_dialog(
        self,
        "Select Situation",
        SITUATION_OPTIONS,
        lambda situation: show_shot_type_dialog(self, x, y, phase, situation, shot_or_goal),
        SITUATION_DIALOG_SIZE,
    )


def show_shot_type_dialog(self, x, y, phase, situation, shot_or_goal):
    show_option_dialog(
        self,
        "Select Shot Type",
        SHOT_TYPE_OPTIONS,
        lambda shot_type: show_shooter_hand_dialog(
            self, x, y, phase, situation, shot_type, shot_or_goal
        ),
        SHOT_TYPE_DIALOG_SIZE,
    )


def show_shooter_hand_dialog(self, x, y, phase, situation, shot_type, shot_or_goal):
    def handle(shooter):
        unassisted = situation in ("Free shot", "Penalty Shot") or shot_type in ("Free shot", "Penalty Shot")
        if unassisted:
            finalize_event(self, x, y, phase, situation, shot_type, "", shooter, shot_or_goal)
        else:
            show_passer_hand_dialog(self, x, y, phase, situation, shot_type, shooter, shot_or_goal)

    show_option_dialog(
        self,
        "Shooter Stick Hand",
        HAND_OPTIONS,
        handle,
        HAND_DIALOG_SIZE,
    )


def show_passer_hand_dialog(self, x, y, phase, situation, shot_type, shooter, shot_or_goal):
    show_option_dialog(
        self,
        "Passer Stick Hand",
        HAND_OPTIONS,
        lambda passer: finalize_event(
            self, x, y, phase, situation, shot_type, passer, shooter, shot_or_goal
        ),
        HAND_DIALOG_SIZE,
    )


# --- Special case (keep separate) ---

def show_pass_origin_dialog(self, x, y, phase, situation, shot_type, passer, shooter):
    popup = tk.Toplevel(self.root)
    popup.title("Mark Pass Origin?")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())
    popup.bind("<Destroy>", lambda _: setattr(self, "popup_open", False))

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    tk.Label(
        frame,
        text="Do you want to place a pass origin point?",
        wraplength=250,
        justify="center",
    ).pack(pady=(0, 15))

    tk.Button(
        frame,
        text="Yes (mark manually)",
        bg="#27ae60",
        fg="white",
        command=lambda: [
            popup.destroy(),
            setattr(self, "pending_pass_data", (x, y, phase, situation, shot_type, passer, shooter)),
            setattr(self, "expecting_pass_click", True),
        ],
    ).pack(fill=tk.X, pady=(0, 8))

    tk.Button(
        frame,
        text="No (skip pass origin)",
        bg="#c0392b",
        fg="white",
        command=lambda: [
            popup.destroy(),
            self.add_shot_event(x, y, phase, situation, shot_type, passer, shooter),
        ],
    ).pack(fill=tk.X)

    prepare_popup(popup, self, *PASS_ORIGIN_DIALOG_SIZE)