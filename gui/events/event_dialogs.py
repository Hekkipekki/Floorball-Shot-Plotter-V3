import tkinter as tk

from gui.events.popup_utils import prepare_popup
from gui.events.event_finalize import finalize_event


PHASE_GROUPS = {
    "5v5 / Even strength": {
        "description": "Opponent shot against your team during normal even-strength play.",
        "sub_phases": {
            "Opponent controlled entry": "Opponent enters your defensive zone with the ball before the shot.",
            "Opponent settled offense": "Opponent has established possession in your defensive zone.",
            "Opponent transition / rush": "Opponent creates the shot from a quick transition or rush.",
            "Defensive turnover against": "Your team loses the ball and the opponent shoots from the turnover.",
        },
    },
    "Special teams": {
        "description": "Opponent shot against your team during power play, box play, or goalie-pulled situations.",
        "sub_phases": {
            "Opponent power play": "Opponent is attacking with a player advantage.",
            "Opponent box play / shorthanded": "Opponent is shorthanded but still creates a shot.",
            "Opponent 6v5 / goalie pulled": "Opponent has pulled the goalkeeper for an extra attacker.",
            "Against empty net": "Opponent shoots at your empty net.",
        },
    },
    "Restart / set play against": {
        "description": "Opponent shot against your team from a static restart or set play.",
        "sub_phases": {
            "Free hit against": "Opponent creates a shot from a free hit/free shot restart.",
            "Faceoff against": "Opponent creates a shot directly or shortly after a faceoff.",
            "Penalty shot against": "Opponent penalty-shot attempt against your goalkeeper.",
        },
    },
    "Broken play / rebound against": {
        "description": "Opponent shot against your team from chaos, rebounds, or loose-ball situations.",
        "sub_phases": {
            "Rebound against": "Opponent shoots after a save, block, or loose rebound.",
            "Screen / traffic against": "Opponent shot with traffic or screen in front of the goalkeeper.",
            "Loose ball / scramble against": "Opponent shot from a loose-ball or crease-scramble situation.",
            "Blocked shot second chance": "Opponent gets another chance after a blocked shot.",
        },
    },
}


SITUATION_OPTIONS_BY_SUB_PHASE = {
    "Opponent controlled entry": {
        "Controlled entry shot": "Opponent enters with control and shoots from the entry.",
        "Wide entry shot": "Opponent enters wide and creates a shot from the side lane.",
        "Middle-lane entry": "Opponent attacks the middle lane on entry before shooting.",
        "Drop / trailer on entry": "Opponent uses a drop pass or late trailer before the shot.",
    },
    "Opponent settled offense": {
        "Point shot": "Opponent shoots from high or near the defensive-zone line.",
        "Slot pass": "Opponent passes into the slot before the shot.",
        "Cross-pass": "Opponent creates lateral movement before the shot.",
        "Low-high": "Opponent moves the ball from low/deep to a higher shooter.",
        "Behind-net play": "Opponent uses a play from behind or beside the goal.",
        "Cycle / long possession": "Opponent creates the shot after longer possession.",
    },
    "Opponent transition / rush": {
        "Breakaway against": "Opponent gets free alone against the goalkeeper.",
        "2v1 against": "Opponent creates a two-against-one rush.",
        "3v2 against": "Opponent creates a three-against-two rush.",
        "Odd-man rush against": "Opponent creates any other numerical rush advantage.",
        "Quick counter shot": "Opponent shoots quickly after transition.",
        "Trailer shot against": "Opponent late trailer receives the ball and shoots.",
    },
    "Defensive turnover against": {
        "Lost ball low": "Your team loses possession low/deep in the defensive zone.",
        "Lost ball middle": "Your team loses possession in the central defensive-zone area.",
        "Failed zone exit": "Your team fails to exit and the opponent shoots.",
        "Bad pass intercepted": "Opponent intercepts a pass before shooting.",
        "Pressure turnover against": "Opponent pressure forces the turnover before the shot.",
    },
    "Opponent power play": {
        "Power-play point shot": "Opponent power-play shot from high/point position.",
        "Power-play cross-pass": "Opponent power-play shot after lateral ball movement.",
        "Power-play slot pass": "Opponent power-play pass into the slot before the shot.",
        "Power-play screen": "Opponent power-play shot through traffic/screen.",
        "Power-play rebound": "Opponent power-play rebound chance.",
    },
    "Opponent box play / shorthanded": {
        "Shorthanded rush against": "Opponent creates a shorthanded transition/rush chance.",
        "Shorthanded turnover": "Opponent creates a shorthanded shot after winning the ball.",
        "Clearance becomes shot": "Opponent clearance or pressure turns into a shot chance.",
    },
    "Opponent 6v5 / goalie pulled": {
        "6v5 point shot": "Opponent 6v5 shot from high/point position.",
        "6v5 slot pass": "Opponent 6v5 pass into the slot before the shot.",
        "6v5 screen": "Opponent 6v5 shot through traffic/screen.",
        "6v5 rebound": "Opponent 6v5 rebound chance.",
    },
    "Against empty net": {
        "Empty-net shot against": "Opponent shoots at your empty net.",
        "Empty-net long shot": "Opponent attempts a longer empty-net shot.",
        "Empty-net tap-in": "Opponent gets a close empty-net finish.",
    },
    "Free hit against": {
        "Direct free hit": "Opponent shoots directly from the restart.",
        "Set play against": "Opponent runs a prepared free-hit play.",
        "Free-hit screen": "Opponent free-hit shot with screen/traffic.",
        "Pass before free-hit shot": "Opponent passes before shooting from the restart.",
    },
    "Faceoff against": {
        "Clean faceoff shot": "Opponent wins the faceoff directly to a shot.",
        "Faceoff set play": "Opponent creates the shot from a faceoff pattern.",
        "Faceoff scramble": "Opponent shot follows a loose-ball faceoff scramble.",
    },
    "Penalty shot against": {
        "Penalty shot": "Opponent penalty-shot attempt.",
    },
    "Rebound against": {
        "Shot rebound": "Opponent shoots after a goalkeeper save or rebound.",
        "Blocked-shot rebound": "Opponent shoots after a block rebounds loose.",
        "Loose rebound in slot": "Opponent finds a rebound in the slot.",
        "Goal-mouth rebound": "Opponent chance around the goal mouth.",
    },
    "Screen / traffic against": {
        "Goalkeeper screened": "Goalkeeper's vision is blocked on the shot.",
        "Traffic in slot": "Opponent shot through traffic in the slot.",
        "Deflection / tip against": "Opponent redirects the shot near the goal.",
    },
    "Loose ball / scramble against": {
        "Crease scramble": "Opponent chance from a messy goal-area scramble.",
        "Loose ball": "Opponent shoots after a loose ball.",
        "Broken coverage": "Your defensive coverage breaks down before the shot.",
        "Failed clearance": "Your team fails to clear before the opponent shot.",
    },
    "Blocked shot second chance": {
        "Second chance shot": "Opponent gets a second shot after the first is blocked.",
        "Block rebound to slot": "Blocked ball rebounds into a dangerous central area.",
        "Reset after block": "Opponent recovers the block and shoots again after a small reset.",
    },
}


SHOT_TYPE_OPTIONS = {
    "One-timer": "Direct shot immediately after receiving the ball.",
    "Wrist shot": "Standard controlled wrist or sweep release.",
    "Slapshot": "Power shot with full backswing.",
    "Backhand": "Shot released from the backhand side.",
    "Snap shot": "Quick release between wrist shot and slapshot.",
    "Controlled shot": "Composed shot with extra control and time.",
    "Deke": "Player attempts to beat the goalkeeper with a move.",
    "Deflection": "Shot redirected by stick or body.",
    "Tip-in": "Close-range redirect near the goal crease.",
    "Rebound poke": "Loose rebound finished quickly near goal.",
    "Bounce shot": "Shot intentionally or unintentionally bouncing.",
    "Empty net": "Shot against an empty net.",
    "Free shot": "Direct shot from a restart/free-hit.",
    "Penalty shot": "Penalty-shot attempt.",
    "Own Goal": "Ball directed into own net by defending team.",
}


SHOOTER_HAND_OPTIONS = {
    "Left": "Opponent shooter stick blade on the left side.",
    "Right": "Opponent shooter stick blade on the right side.",
}


PASSER_HAND_OPTIONS = {
    "Left": "Opponent passer stick blade on the left side.",
    "Right": "Opponent passer stick blade on the right side.",
    "No assist": "Opponent shot was unassisted.",
}

DIALOG_BG = "#223344"
DIALOG_BTN_BG = "#4A9BE8"
DIALOG_BACK_BG = "#445566"
DIALOG_TEXT = "white"
OPTION_ROW_HEIGHT = 36
DIALOG_VERTICAL_CHROME = 108
DIALOG_NAV_HEIGHT = 76
DIALOG_DESC_HEIGHT = 46
MAX_DIALOG_HEIGHT = 620


def _create_base_popup(app, title, on_destroy=None):
    popup = tk.Toplevel(app.root)
    popup.title(title)
    popup.transient(app.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())

    if on_destroy is not None:
        popup.bind("<Destroy>", lambda _: on_destroy())

    frame = tk.Frame(popup, bg=DIALOG_BG)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    return popup, frame


def _dialog_height(option_count: int, requested_height: int, has_back: bool) -> int:
    content_height = option_count * OPTION_ROW_HEIGHT + DIALOG_VERTICAL_CHROME
    if has_back:
        content_height += 36
    return min(max(220, min(content_height, requested_height)), MAX_DIALOG_HEIGHT)


def _make_scrollable_options(parent, height: int):
    container = tk.Frame(parent, bg=DIALOG_BG)
    container.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(container, bg=DIALOG_BG, highlightthickness=0, borderwidth=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    options_frame = tk.Frame(canvas, bg=DIALOG_BG)
    window_id = canvas.create_window((0, 0), window=options_frame, anchor="nw")

    def on_configure(_event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.itemconfigure(window_id, width=canvas.winfo_width())

    options_frame.bind("<Configure>", on_configure)
    canvas.bind("<Configure>", on_configure)
    canvas.configure(yscrollcommand=scrollbar.set, height=height)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    return options_frame, canvas


def _bind_mousewheel(widget, canvas):
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    widget.bind_all("<MouseWheel>", on_mousewheel)
    widget.bind_all("<Button-4>", lambda _event: canvas.yview_scroll(-1, "units"))
    widget.bind_all("<Button-5>", lambda _event: canvas.yview_scroll(1, "units"))


def show_option_dialog(
    app,
    title,
    options,
    on_select,
    width=320,
    height=300,
    on_destroy=None,
    on_back=None,
):
    popup_height = _dialog_height(len(options), height, on_back is not None)
    popup, frame = _create_base_popup(app, title, on_destroy=on_destroy)

    desc_label = tk.Label(
        frame,
        text="Hover an option to see details.",
        bg=DIALOG_BG,
        fg=DIALOG_TEXT,
        wraplength=max(220, width - 45),
        justify="center",
        anchor="center",
        height=2,
    )
    desc_label.pack(fill=tk.X, pady=(0, 8))

    option_area_height = max(90, popup_height - DIALOG_DESC_HEIGHT - DIALOG_NAV_HEIGHT)
    options_frame, canvas = _make_scrollable_options(frame, option_area_height)
    _bind_mousewheel(popup, canvas)

    for label, description in options.items():
        btn = tk.Button(
            options_frame,
            text=label,
            bg=DIALOG_BTN_BG,
            fg=DIALOG_TEXT,
            activebackground="#5AADF2",
            activeforeground=DIALOG_TEXT,
            relief=tk.FLAT,
            padx=10,
            pady=5,
            anchor="center",
            justify="center",
            font=("Arial", 9, "bold"),
            command=lambda value=label: [popup.destroy(), on_select(value)],
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda _e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda _e: desc_label.config(text="Hover an option to see details."))

    nav_frame = tk.Frame(frame, bg=DIALOG_BG)
    nav_frame.pack(fill=tk.X, pady=(8, 0))

    if on_back is not None:
        back = tk.Button(
            nav_frame,
            text="← Back",
            bg=DIALOG_BACK_BG,
            fg=DIALOG_TEXT,
            activebackground="#526679",
            activeforeground=DIALOG_TEXT,
            relief=tk.FLAT,
            font=("Arial", 9, "bold"),
            command=lambda: [popup.destroy(), on_back()],
        )
        back.pack(fill=tk.X, pady=(0, 5))

    cancel = tk.Button(
        nav_frame,
        text="Cancel",
        bg=DIALOG_BTN_BG,
        fg=DIALOG_TEXT,
        activebackground="#5AADF2",
        activeforeground=DIALOG_TEXT,
        relief=tk.FLAT,
        font=("Arial", 9),
        command=popup.destroy,
    )
    cancel.pack(fill=tk.X)

    prepare_popup(popup, app, width=width, height=popup_height)


def show_phase_dialog(self, x, y, shot_or_goal):
    if self.popup_open:
        return

    self.popup_open = True

    group_options = {
        group: data["description"]
        for group, data in PHASE_GROUPS.items()
    }

    show_option_dialog(
        self,
        title="Opponent Shot/Goal: Select Game State",
        options=group_options,
        on_select=lambda phase_group: show_sub_phase_dialog(
            self, x, y, shot_or_goal, phase_group
        ),
        width=360,
        height=320,
        on_destroy=lambda: setattr(self, "popup_open", False),
    )


def show_phase_dialog_after_back(self, x, y, shot_or_goal):
    self.popup_open = False
    show_phase_dialog(self, x, y, shot_or_goal)


def show_sub_phase_dialog(self, x, y, shot_or_goal, phase_group):
    sub_options = PHASE_GROUPS[phase_group]["sub_phases"]

    show_option_dialog(
        self,
        title=f"{phase_group}: Select Opponent Context",
        options=sub_options,
        on_select=lambda sub_phase: show_situation_dialog(
            self, x, y, shot_or_goal, phase_group, sub_phase
        ),
        width=390,
        height=370,
        on_back=lambda: show_phase_dialog_after_back(self, x, y, shot_or_goal),
    )


def show_situation_dialog(self, x, y, shot_or_goal, phase_group, sub_phase):
    saved_phase = f"{phase_group} - {sub_phase}"

    situation_options = SITUATION_OPTIONS_BY_SUB_PHASE.get(
        sub_phase,
        {
            "General chance against": "General opponent scoring chance against your team.",
            "Rebound against": "Opponent shot opportunity following a saved or blocked shot.",
            "Screen against": "Opponent shot where the goalkeeper's vision is blocked.",
        },
    )

    show_option_dialog(
        self,
        title="Select Opponent Shot Situation",
        options=situation_options,
        on_select=lambda situation: show_shot_type_dialog(
            self,
            x,
            y,
            saved_phase,
            situation,
            shot_or_goal,
            phase_group,
            sub_phase,
        ),
        width=380,
        height=430,
        on_back=lambda: show_sub_phase_dialog(self, x, y, shot_or_goal, phase_group),
    )


def show_shot_type_dialog(self, x, y, phase, situation, shot_or_goal, phase_group, sub_phase):
    show_option_dialog(
        self,
        title="Select Opponent Shot Type",
        options=SHOT_TYPE_OPTIONS,
        on_select=lambda shot_type: show_shooter_hand_dialog(
            self,
            x,
            y,
            phase,
            situation,
            shot_type,
            shot_or_goal,
            phase_group,
            sub_phase,
        ),
        width=360,
        height=620,
        on_back=lambda: show_situation_dialog(
            self, x, y, shot_or_goal, phase_group, sub_phase
        ),
    )


def show_shooter_hand_dialog(
    self,
    x,
    y,
    phase,
    situation,
    shot_type,
    shot_or_goal,
    phase_group,
    sub_phase,
):
    def handle_selection(shooter_hand):
        unassisted = (
            situation in ("Direct free shot", "Penalty Shot", "Penalty shot", "Free shot")
            or shot_type in ("Free shot", "Penalty shot")
        )
        if unassisted:
            finalize_event(
                self,
                x,
                y,
                phase,
                situation,
                shot_type,
                "No assist",
                shooter_hand,
                shot_or_goal,
            )
        else:
            show_passer_hand_dialog(
                self,
                x,
                y,
                phase,
                situation,
                shot_type,
                shooter_hand,
                shot_or_goal,
                phase_group,
                sub_phase,
            )

    show_option_dialog(
        self,
        title="Select Opponent Shooter Hand",
        options=SHOOTER_HAND_OPTIONS,
        on_select=handle_selection,
        width=300,
        height=250,
        on_back=lambda: show_shot_type_dialog(
            self, x, y, phase, situation, shot_or_goal, phase_group, sub_phase
        ),
    )


def show_passer_hand_dialog(
    self,
    x,
    y,
    phase,
    situation,
    shot_type,
    shooter_hand,
    shot_or_goal,
    phase_group,
    sub_phase,
):
    show_option_dialog(
        self,
        title="Select Opponent Passer Hand",
        options=PASSER_HAND_OPTIONS,
        on_select=lambda passer_hand: finalize_event(
            self,
            x,
            y,
            phase,
            situation,
            shot_type,
            passer_hand,
            shooter_hand,
            shot_or_goal,
        ),
        width=300,
        height=280,
        on_back=lambda: show_shooter_hand_dialog(
            self, x, y, phase, situation, shot_type, shot_or_goal, phase_group, sub_phase
        ),
    )
