import tkinter as tk

from core.xg_context import (
    CHANCE_TYPE_OPTIONS,
    GOALIE_STATE_OPTIONS,
    PRESSURE_OPTIONS,
    SCREEN_OPTIONS,
    STRENGTH_OPTIONS,
    infer_xg_context_defaults,
    normalize_xg_context,
)
from gui.events.event_finalize import finalize_event
from gui.events.popup_utils import prepare_popup

DIALOG_BG = "#223344"
DIALOG_TEXT = "white"
DIALOG_BTN_BG = "#4A9BE8"
DIALOG_BACK_BG = "#445566"
DIALOG_WIDTH = 520
DIALOG_HEIGHT = 620


def _radio_group(parent, title: str, variable: tk.StringVar, options) -> None:
    frame = tk.LabelFrame(parent, text=title, bg=DIALOG_BG, fg=DIALOG_TEXT, padx=8, pady=6)
    frame.pack(fill=tk.X, pady=5)
    for option in options:
        tk.Radiobutton(
            frame,
            text=option,
            variable=variable,
            value=option,
            bg=DIALOG_BG,
            fg=DIALOG_TEXT,
            selectcolor=DIALOG_BG,
            activebackground=DIALOG_BG,
            activeforeground=DIALOG_TEXT,
            anchor="w",
        ).pack(anchor="w")


def show_xg_context_dialog(app, x, y, phase, situation, shot_type, passer, shooter, shot_or_goal):
    defaults = infer_xg_context_defaults(phase, situation, shot_type)

    popup = tk.Toplevel(app.root)
    popup.title("xG Context")
    popup.transient(app.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda _e: popup.destroy())
    popup.bind("<Destroy>", lambda _: setattr(app, "popup_open", False))

    frame = tk.Frame(popup, bg=DIALOG_BG)
    frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    title = tk.Label(
        frame,
        text="Add xG context (defaults are pre-selected)",
        bg=DIALOG_BG,
        fg=DIALOG_TEXT,
        font=("Arial", 10, "bold"),
    )
    title.pack(fill=tk.X, pady=(0, 8))

    strength_var = tk.StringVar(value=defaults["strength_state"])
    chance_var = tk.StringVar(value=defaults["chance_type"])
    screen_var = tk.StringVar(value=defaults["screen"])
    pressure_var = tk.StringVar(value=defaults["pressure"])
    goalie_var = tk.StringVar(value=defaults["goalie_state"])
    clock_var = tk.StringVar(value=defaults["period_time"])

    _radio_group(frame, "Strength state", strength_var, STRENGTH_OPTIONS)
    _radio_group(frame, "Chance type", chance_var, CHANCE_TYPE_OPTIONS)
    _radio_group(frame, "Screen / traffic", screen_var, SCREEN_OPTIONS)
    _radio_group(frame, "Defensive pressure", pressure_var, PRESSURE_OPTIONS)
    _radio_group(frame, "Goalie state", goalie_var, GOALIE_STATE_OPTIONS)

    clock_frame = tk.Frame(frame, bg=DIALOG_BG)
    clock_frame.pack(fill=tk.X, pady=(8, 10))
    tk.Label(clock_frame, text="Clock (optional, e.g. 12:34):", bg=DIALOG_BG, fg=DIALOG_TEXT).pack(side=tk.LEFT)
    tk.Entry(clock_frame, textvariable=clock_var, width=10).pack(side=tk.LEFT, padx=(8, 0))

    def save_with_context() -> None:
        context = normalize_xg_context(
            {
                "strength_state": strength_var.get(),
                "chance_type": chance_var.get(),
                "screen": screen_var.get(),
                "pressure": pressure_var.get(),
                "goalie_state": goalie_var.get(),
                "period_time": clock_var.get().strip(),
            }
        )
        finalize_event(
            app,
            x,
            y,
            phase,
            situation,
            shot_type,
            passer,
            shooter,
            shot_or_goal,
            popup=popup,
            context=context,
        )

    quick = tk.Button(
        frame,
        text="Save with defaults",
        bg=DIALOG_BTN_BG,
        fg=DIALOG_TEXT,
        relief=tk.FLAT,
        font=("Arial", 9, "bold"),
        command=save_with_context,
    )
    quick.pack(fill=tk.X, pady=(4, 6))

    cancel = tk.Button(
        frame,
        text="Cancel",
        bg=DIALOG_BACK_BG,
        fg=DIALOG_TEXT,
        relief=tk.FLAT,
        command=popup.destroy,
    )
    cancel.pack(fill=tk.X)

    prepare_popup(popup, app, width=DIALOG_WIDTH, height=DIALOG_HEIGHT)
