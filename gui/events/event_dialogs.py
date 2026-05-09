import tkinter as tk

from gui.events.popup_utils import prepare_popup
from gui.events.event_finalize import finalize_event


PHASE_GROUPS = {
    "With ball": {
        "description": "Your team has controlled possession and is trying to attack.",
        "sub_phases": {
            "Zone entry vs full court press": "You are trying to play through or around an aggressive full-court press.",
            "Zone entry": "You are entering the offensive zone against a more organized or passive defense.",
            "Zone offense": "Settled offensive-zone possession where your team is trying to create chances.",
        },
    },
    "Without ball": {
        "description": "The opponent has controlled possession and your team is defending.",
        "sub_phases": {
            "Full court press": "Your team is pressing high to force mistakes or win the ball back early.",
            "Zone entry defense": "Your team is defending while the opponent tries to enter your defensive zone.",
            "Zone defense": "Settled defensive-zone play where the opponent has established possession.",
        },
    },
    "Possession change": {
        "description": "The ball has just changed team and both teams are reorganizing.",
        "sub_phases": {
            "Counter-press": "Your team lost the ball and immediately tries to win it back.",
            "Zone exit": "Your team won the ball and is trying to exit the defensive zone.",
        },
    },
    "Chaos": {
        "description": "Neither team has full tactical control or structure.",
        "sub_phases": {
            "Counter on counter": "One team counters, loses the ball, and the opponent counters back.",
            "Uncontrolled": "Loose-ball, rebound, scramble, broken play or unclear structure.",
        },
    },
    "Free shots": {
        "description": "Static restart situations.",
        "sub_phases": {
            "Free shot for": "Your team has a restart/free shot and can run a set play.",
            "Free shot against": "The opponent has a restart/free shot and your team is defending it.",
        },
    },
}


SITUATION_OPTIONS_BY_SUB_PHASE = {
    "Zone entry vs full court press": {
        "Press break": "Shot chance created after breaking full court pressure.",
        "Turnover forced": "Opponent pressure causes a mistake, leading to a chance.",
        "Quick middle attack": "Fast attack through the middle after beating pressure.",
        "Wide entry attack": "Chance created after entering wide against pressure.",
    },
    "Zone entry": {
        "Controlled entry": "Chance after entering the offensive zone with control.",
        "Rush attack": "Fast attack before the defense is fully set.",
        "Drop pass": "Chance created through a drop pass on entry.",
        "Wide entry attack": "Chance created from the side after entering the zone.",
        "Middle lane attack": "Chance created by attacking the central lane.",
    },
    "Zone offense": {
        "Cross-pass": "Shot after a lateral pass across the defensive structure.",
        "Slot pass": "Pass into the central scoring area before the shot.",
        "Low-high": "Ball moves from low/deep position to a higher shooter.",
        "Screen": "Goalkeeper's vision is blocked.",
        "Rebound": "Shot after a save, block, or loose rebound.",
        "Cycle play": "Chance created through longer settled possession movement.",
    },
    "Full court press": {
        "High steal": "Your team wins the ball high up the court.",
        "Forced turnover": "Opponent loses the ball due to pressure.",
        "Immediate shot": "Shot comes directly after winning the ball.",
        "Trap success": "Chance created after trapping the opponent.",
    },
    "Zone entry defense": {
        "Entry denied turnover": "Your team stops the entry and wins the ball.",
        "Forced wide turnover": "Opponent is forced wide and loses possession.",
        "Counter after entry defense": "Chance created after defending the opponent's entry.",
    },
    "Zone defense": {
        "Defensive-zone turnover": "Your team wins the ball in settled defense.",
        "Blocked shot transition": "Chance comes after blocking a shot.",
        "Rebound clear counter": "Chance after clearing a rebound or loose ball.",
        "Outlet pass": "Chance created by first pass out of defense.",
    },
    "Counter-press": {
        "Immediate regain": "Your team wins the ball back immediately after losing it.",
        "Pressure turnover": "Opponent loses the ball under counter-pressure.",
        "Second wave shot": "Shot after regaining and attacking again quickly.",
    },
    "Zone exit": {
        "Breakaway": "Attacker breaks through alone on the goalkeeper.",
        "2v0": "Two attackers against the goalkeeper without defenders.",
        "2v1": "Two attackers versus one defender.",
        "3v1": "Three attackers versus one defender.",
        "3v2": "Three attackers versus two defenders.",
        "Trailer shot": "Late arriving player gets the shot after the rush.",
        "Fast break": "Quick attack after winning the ball.",
    },
    "Counter on counter": {
        "Breakaway": "Attacker breaks through alone on the goalkeeper.",
        "2v1": "Two attackers versus one defender.",
        "3v2": "Three attackers versus two defenders.",
        "Turnover on rush": "Chance created after stealing the ball during opponent's counter.",
        "Broken rush": "Rush becomes messy but still creates a chance.",
    },
    "Uncontrolled": {
        "Loose ball": "Nobody has full control before the shot.",
        "Crease scramble": "Chaotic chance around the goal area.",
        "Blocked-shot rebound": "Shot comes after a blocked shot bounces loose.",
        "Failed clearance": "Defending team fails to clear the ball.",
        "Broken play": "Structure breaks down before the shot.",
    },
    "Free shot for": {
        "Direct free shot": "Shot directly from the restart.",
        "Set play": "Prepared play from a restart.",
        "Screened free shot": "Free shot with traffic/screen in front.",
        "Pass before shot": "Restart creates a pass before the shot.",
    },
    "Free shot against": {
        "Defended free shot": "Opponent free shot creates a chance against you.",
        "Screened free shot against": "Opponent shot with screen from restart.",
        "Rebound after free shot": "Chance against after the first free shot rebound.",
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
    "Own Goal": "Ball directed into own net by defending team.",
}


SHOOTER_HAND_OPTIONS = {
    "Left": "Shooter stick blade on the left side.",
    "Right": "Shooter stick blade on the right side.",
}


PASSER_HAND_OPTIONS = {
    "Left": "Passer stick blade on the left side.",
    "Right": "Passer stick blade on the right side.",
    "No assist": "Shot was unassisted.",
}


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
        wraplength=300,
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
    width=320,
    height=300,
    on_destroy=None,
    on_back=None,
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

    if on_back is not None:
        back = tk.Button(
            frame,
            text="← Back",
            bg="#445566",
            fg="white",
            relief=tk.RAISED,
            font=("Arial", 9, "bold"),
            command=lambda: [popup.destroy(), on_back()],
        )
        back.pack(fill=tk.X, pady=(0, 5))

    cancel = tk.Button(
        frame,
        text="Cancel",
        bg="#223344",
        fg="white",
        relief=tk.RAISED,
        font=("Arial", 9),
        command=popup.destroy,
    )
    cancel.pack(fill=tk.X, pady=(0, 5))

    prepare_popup(popup, app, width=width, height=height)


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
        title="Select Game Phase",
        options=group_options,
        on_select=lambda phase_group: show_sub_phase_dialog(
            self, x, y, shot_or_goal, phase_group
        ),
        width=330,
        height=300,
        on_destroy=lambda: setattr(self, "popup_open", False),
    )


def show_phase_dialog_after_back(self, x, y, shot_or_goal):
    self.popup_open = False
    show_phase_dialog(self, x, y, shot_or_goal)


def show_sub_phase_dialog(self, x, y, shot_or_goal, phase_group):
    sub_options = PHASE_GROUPS[phase_group]["sub_phases"]

    show_option_dialog(
        self,
        title=f"{phase_group}: Select Sub Phase",
        options=sub_options,
        on_select=lambda sub_phase: show_situation_dialog(
            self, x, y, shot_or_goal, phase_group, sub_phase
        ),
        width=360,
        height=320,
        on_back=lambda: show_phase_dialog_after_back(self, x, y, shot_or_goal),
    )


def show_situation_dialog(self, x, y, shot_or_goal, phase_group, sub_phase):
    saved_phase = f"{phase_group} - {sub_phase}"

    situation_options = SITUATION_OPTIONS_BY_SUB_PHASE.get(
        sub_phase,
        {
            "General chance": "General scoring chance.",
            "Rebound": "Shot opportunity following a saved or blocked shot.",
            "Screen": "Shot where the goalkeeper's vision is blocked.",
        },
    )

    show_option_dialog(
        self,
        title="Select Situation",
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
        width=360,
        height=390,
        on_back=lambda: show_sub_phase_dialog(self, x, y, shot_or_goal, phase_group),
    )


def show_shot_type_dialog(self, x, y, phase, situation, shot_or_goal, phase_group, sub_phase):
    show_option_dialog(
        self,
        title="Select Shot Type",
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
        width=330,
        height=520,
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
            situation in ("Direct free shot", "Penalty Shot", "Free shot")
            or shot_type in ("Free shot",)
        )

        if unassisted:
            finalize_event(
                self,
                x,
                y,
                phase,
                situation,
                shot_type,
                "",
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
        title="Shooter Stick Hand",
        options=SHOOTER_HAND_OPTIONS,
        on_select=handle_selection,
        width=280,
        height=170,
        on_back=lambda: show_shot_type_dialog(
            self,
            x,
            y,
            phase,
            situation,
            shot_or_goal,
            phase_group,
            sub_phase,
        ),
    )


def show_passer_hand_dialog(
    self,
    x,
    y,
    phase,
    situation,
    shot_type,
    shooter,
    shot_or_goal,
    phase_group,
    sub_phase,
):
    def handle_selection(passer_hand):
        passer_value = "" if passer_hand == "No assist" else passer_hand

        finalize_event(
            self,
            x,
            y,
            phase,
            situation,
            shot_type,
            passer_value,
            shooter,
            shot_or_goal,
        )

    show_option_dialog(
        self,
        title="Passer Stick Hand",
        options=PASSER_HAND_OPTIONS,
        on_select=handle_selection,
        width=280,
        height=210,
        on_back=lambda: show_shooter_hand_dialog(
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
        bg="#223344",
        fg="white",
        font=("Arial", 9, "bold"),
        command=lambda: [
            popup.destroy(),
            setattr(
                self,
                "pending_pass_data",
                (x, y, phase, situation, shot_type, passer, shooter),
            ),
            setattr(self, "expecting_pass_click", True),
        ],
    )
    btn_yes.pack(fill=tk.X, pady=(0, 8))

    btn_no = tk.Button(
        frame,
        text="No (skip pass origin)",
        bg="#223344",
        fg="white",
        font=("Arial", 9, "bold"),
        command=lambda: [
            popup.destroy(),
            self.add_shot_event(x, y, phase, situation, shot_type, passer, shooter),
        ],
    )
    btn_no.pack(fill=tk.X)

    prepare_popup(popup, self, width=320, height=150)