import os
import tkinter as tk
from data.match_store import load_all_matches

def load_season_matches(app):
    games_dir = os.path.join(app.project_root, "Games")
    subfolders = [
        name for name in os.listdir(games_dir)
        if os.path.isdir(os.path.join(games_dir, name))
    ]

    if not subfolders:
        load_all_matches(app, games_dir)
        app.current_match.set("Season")
        app.load_selected_match()
        return

    options = ["Games (all matches in root)"] + subfolders
    selected = show_selection_dialog(app.root, "Select folder to load matches from:", options)

    if selected:
        folder = games_dir if selected == "Games (all matches in root)" else os.path.join(games_dir, selected)
        load_all_matches(app, folder)
        app.current_match.set("Season")
        app.load_selected_match()

def show_selection_dialog(parent, title, options):
    result = {"choice": None}

    win = tk.Toplevel(parent)
    win.title(title)
    win.grab_set()
    win.resizable(False, False)

    tk.Label(win, text=title).pack(padx=10, pady=(10, 5))
    var = tk.StringVar(value=options[0])

    for opt in options:
        tk.Radiobutton(win, text=opt, variable=var, value=opt).pack(anchor="w", padx=20)

    def submit():
        result["choice"] = var.get()
        win.destroy()

    def cancel():
        win.destroy()

    button_frame = tk.Frame(win)
    button_frame.pack(pady=(10, 10))
    tk.Button(button_frame, text="OK", command=submit, width=10).pack(side="left", padx=5)
    tk.Button(button_frame, text="Cancel", command=cancel, width=10).pack(side="left", padx=5)

    win.wait_window()
    return result["choice"]
