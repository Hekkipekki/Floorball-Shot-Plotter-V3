import tkinter as tk
from tkinter import messagebox

# --- Centrering och popup-hantering ---

def center_popup_in_canvas(app, width=260, height=220, top_offset=150):
    canvas_widget = app.canvas.get_tk_widget()
    canvas_widget.update_idletasks()
    x_canvas = canvas_widget.winfo_rootx()
    y_canvas = canvas_widget.winfo_rooty()
    canvas_width = canvas_widget.winfo_width()
    x = x_canvas + (canvas_width - width) // 2
    y = y_canvas + top_offset
    return x, y

def format_geometry_string(width, height, x, y):
    return f"{width}x{height}+{x}+{y}"

def prepare_popup(popup, app, width=260, height=220, top_offset=400):
    popup.withdraw()
    popup.update_idletasks()
    x, y = center_popup_in_canvas(app, width, height, top_offset)
    popup.geometry(format_geometry_string(width, height, x, y))
    popup.deiconify()

# --- Space för att radera punkt ---

def on_space_key_pressed(app, event):
    canvas_widget = app.canvas.get_tk_widget()
    mouse_x = canvas_widget.winfo_pointerx() - canvas_widget.winfo_rootx()
    mouse_y = canvas_widget.winfo_pointery() - canvas_widget.winfo_rooty()
    canvas_height = canvas_widget.winfo_height()
    corrected_mouse_y = canvas_height - mouse_y
    app.remove_nearest_point(mouse_x, corrected_mouse_y)

# --- Klick på canvasen ---

def onclick(self, event):
    if self.view_mode.get() != "Plot":
        print("⛔ Cannot place shots/goals outside of Plot view mode.")
        return
    if not event.xdata or not event.ydata or self.popup_open:
        return

    if getattr(self, "expecting_pass_click", False):
        self.expecting_pass_click = False
        if hasattr(self, "pending_pass_data"):
            main_x, main_y, phase, situation, shot_type, passer, shooter = self.pending_pass_data
            pass_x = int(round(event.xdata))
            pass_y = int(round(event.ydata))
            self.add_shot_event(main_x, main_y, phase, situation, shot_type, passer, shooter, pass_x=pass_x, pass_y=pass_y)
            del self.pending_pass_data
        return

    if event.button == 1:
        show_phase_dialog(self, event.xdata, event.ydata, shot_or_goal="shot")
    elif event.button == 3:
        show_phase_dialog(self, event.xdata, event.ydata, shot_or_goal="goal")

# --- Dialogsteg ---

def show_phase_dialog(self, x, y, shot_or_goal):
    if self.popup_open:
        return
    self.popup_open = True

    popup = tk.Toplevel(self.root)
    popup.title("Select Phase")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Destroy>", lambda _: setattr(self, "popup_open", False))
    popup.bind("<Escape>", lambda e: popup.destroy())

    phases = {
        "Full Court press": "Trying to activate from the normal entry defense, up to a full court press.",
        "Zone entry defense": "The team is playing the normal defense system, trying to prevent the opponent from playing a zone entry with quality.",
        "Zone Defense": "You are trying to defend after the opponent has settled in playing zone offense.",
        "Zone Exit": "The opponent activates counter-press after you have won the ball in your own zone.",
        "Counter on counter": "When a team counters after having won the ball from the opponent's counter-attack.",
        "Uncontrolled": "When a situation cannot be placed under any other game situation.",
    }

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    desc_label = tk.Label(frame, text="", wraplength=250, justify="center", anchor='center')
    desc_label.pack_forget()

    for phase, description in phases.items():
        btn = tk.Button(
            frame, text=phase, bg="#223344", fg="white", relief=tk.RAISED,
            padx=10, pady=5, anchor="center", justify="center", font=("Arial", 9, "bold"),
            command=lambda p=phase: [popup.destroy(), show_situation_dialog(self, x, y, p, shot_or_goal)]
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda e: desc_label.config(text=""))

    desc_label.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
    cancel = tk.Button(frame, text="Cancel", command=popup.destroy)
    cancel.pack(fill=tk.X, pady=(0, 5))
    prepare_popup(popup, self, width=265, height=350)

def show_situation_dialog(self, x, y, phase, shot_or_goal):
    popup = tk.Toplevel(self.root)
    popup.title("Select Situation")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())

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

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    desc_label = tk.Label(frame, text="", wraplength=250, justify="center", anchor="center")
    desc_label.pack_forget()

    for label, description in situations.items():
        btn = tk.Button(
            frame, text=label, bg="#223344", fg="white", relief=tk.RAISED,
            padx=10, pady=5, anchor="center", justify="center", font=("Arial", 9, "bold"),
            command=lambda l=label: [popup.destroy(), show_shot_type_dialog(self, x, y, phase, l, shot_or_goal)]
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda e: desc_label.config(text=""))

    desc_label.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
    cancel = tk.Button(frame, text="Cancel", command=popup.destroy)
    cancel.pack(fill=tk.X, pady=(0, 5))
    prepare_popup(popup, self, width=265, height=370)

def show_shot_type_dialog(self, x, y, phase, situation, shot_or_goal):
    popup = tk.Toplevel(self.root)
    popup.title("Select Shot Type")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())

    shot_types = {
        "One-timer": "A direct shot taken immediately after receiving the ball.",
        "Controlled shot": "A composed, aimed shot with time and balance.",
        "Own Goal": "Shot directed by defending team into their own net.",
        "Deke": "A deceptive move to fake out the goalie before shooting.",
        "Deflection": "A shot redirected by a player’s stick or body after an initial shot or pass.",
        "Penalty Shot": "Awarded direct shot from penalty mark.",
        "Free shot": "Direct Shot, no passes.",
    }

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    desc_label = tk.Label(frame, text="", wraplength=250, justify="center", anchor="center")
    desc_label.pack_forget()

    for label, description in shot_types.items():
        btn = tk.Button(
            frame, text=label, bg="#223344", fg="white", relief=tk.RAISED,
            padx=10, pady=5, anchor="center", justify="center", font=("Arial", 9, "bold"),
            command=lambda l=label: [popup.destroy(), show_shooter_hand_dialog(self, x, y, phase, situation, l, shot_or_goal)]
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda e: desc_label.config(text=""))

    desc_label.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
    cancel = tk.Button(frame, text="Cancel", command=popup.destroy)
    cancel.pack(fill=tk.X, pady=(0, 5))
    prepare_popup(popup, self, width=265, height=320)

def show_shooter_hand_dialog(self, x, y, phase, situation, shot_type, shot_or_goal):
    popup = tk.Toplevel(self.root)
    popup.title("Shooter Stick Hand")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())

    hands = {
        "Left": "Shooter holds the stick on the left side.",
        "Right": "Shooter holds the stick on the right side."
    }

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    desc_label = tk.Label(frame, text="", wraplength=250, justify="center", anchor='center')
    desc_label.pack_forget()

    for hand, description in hands.items():
        def handle_selection(h=hand):
            popup.destroy()
            # 🔁 Skip Passer-hand if shot is unassisted
            unassisted = situation in ("Free shot", "Penalty Shot") or shot_type in ("Free shot", "Penalty Shot")
            if unassisted:
                finalize_event(self, x, y, phase, situation, shot_type, "", h, shot_or_goal)
            else:
                show_passer_hand_dialog(self, x, y, phase, situation, shot_type, h, shot_or_goal)

        btn = tk.Button(
            frame, text=hand, bg="#223344", fg="white", relief=tk.RAISED,
            padx=10, pady=5, anchor="center", justify="center", font=("Arial", 9, "bold"),
            command=handle_selection
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda e: desc_label.config(text=""))

    desc_label.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
    cancel = tk.Button(frame, text="Cancel", command=popup.destroy)
    cancel.pack(fill=tk.X, pady=(0, 5))
    prepare_popup(popup, self, width=265, height=150)


def show_passer_hand_dialog(self, x, y, phase, situation, shot_type, shooter, shot_or_goal):
    popup = tk.Toplevel(self.root)
    popup.title("Passer Stick Hand")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())

    hands = {
        "Left": "Passer holds the stick on the left side.",
        "Right": "Passer holds the stick on the right side."
    }

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    desc_label = tk.Label(frame, text="", wraplength=250, justify="center", anchor='center')
    desc_label.pack_forget()

    for hand, description in hands.items():
        btn = tk.Button(
            frame, text=hand, bg="#223344", fg="white", relief=tk.RAISED,
            padx=10, pady=5, anchor="center", justify="center", font=("Arial", 9, "bold"),
            command=lambda h=hand: [popup.destroy(), finalize_event(self, x, y, phase, situation, shot_type, h, shooter, shot_or_goal)]
        )
        btn.pack(fill=tk.X, pady=3)
        btn.bind("<Enter>", lambda e, txt=description: desc_label.config(text=txt))
        btn.bind("<Leave>", lambda e: desc_label.config(text=""))

    desc_label.pack(fill=tk.BOTH, expand=True, pady=(10, 5))
    cancel = tk.Button(frame, text="Cancel", command=popup.destroy)
    cancel.pack(fill=tk.X, pady=(0, 5))
    prepare_popup(popup, self, width=265, height=150)

def show_pass_origin_dialog(self, x, y, phase, situation, shot_type, passer, shooter):
    popup = tk.Toplevel(self.root)
    popup.title("Mark Pass Origin?")
    popup.transient(self.root)
    popup.grab_set()
    popup.bind("<Escape>", lambda e: popup.destroy())
    popup.bind("<Destroy>", lambda _: setattr(self, "popup_open", False))

    frame = tk.Frame(popup)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    label = tk.Label(frame, text="Do you want to place a pass origin point?",
                     wraplength=250, justify="center", font=("Arial", 9, "bold"))
    label.pack(pady=(0, 15))

    btn_yes = tk.Button(frame, text="Yes (mark manually)", bg="#27ae60", fg="white",
                        font=("Arial", 8, "bold"),
                        command=lambda: [
                            popup.destroy(),
                            setattr(self, "pending_pass_data", (x, y, phase, situation, shot_type, passer, shooter)),
                            setattr(self, "expecting_pass_click", True)
                        ])
    btn_yes.pack(fill=tk.X, pady=(0, 8))

    btn_no = tk.Button(frame, text="No (skip pass origin)", bg="#c0392b", fg="white",
                       font=("Arial", 10, "bold"),
                       command=lambda: [
                           popup.destroy(),
                           self.add_shot_event(x, y, phase, situation, shot_type, passer, shooter)
                       ])
    btn_no.pack(fill=tk.X)

    prepare_popup(popup, self, width=300, height=120)

# --- Finalisering ---

def finalize_event(app, x, y, phase, situation, shot_type, passer, shooter, shot_or_goal, popup=None):
    x = int(round(x))
    y = int(round(y))

    if popup:
        popup.destroy()

    if app.view_mode.get() != "Plot":
        print("⛔ Cannot place shots outside of Plot view.")
        return

    if shot_or_goal == "goal":
        app.add_goal_event(x, y, phase, situation, shot_type, passer, shooter)
    else:
        if situation == "Penalty Shot" or shot_type == "Free shot":
            # Direkt logga utan passpunkt
            app.add_shot_event(x, y, phase, situation, shot_type, passer, shooter)
        else:
            show_pass_origin_dialog(app, x, y, phase, situation, shot_type, passer, shooter)
