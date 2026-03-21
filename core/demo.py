import random
from gui.messages import show_temporary_message

def generate_demo_shots(app):
    if app.view_mode.get() != "Plot":
        print("⛔ Cannot generate demo shots outside of Plot view mode.")
        show_temporary_message(app, "⛔ Switch to 'Plot' mode to add demo shots.")
        return

    print("🔁 Generating demo shots...")

    current_match = app.current_match.get()

    # ✅ Faser enligt dialogen
    phases = [
        "Full Court press", "Zone entry defense", "Zone Defense",
        "Zone Exit", "Counter on counter", "Uncontrolled"
    ]

    # ✅ Situationer enligt dialogen
    situations = [
        "Breakaway", "2v0", "2v1", "3v1", "3v2",
        "Rebound", "Penalty Shot", "Free shot"
    ]

    # ✅ Skottyper enligt dialogen
    shot_types = [
        "One-timer", "Controlled shot", "Own Goal",
        "Deke", "Deflection"
    ]

    hands = ["Left", "Right"]
    periods = ["1", "2", "3", "OT"]

    width = 1455
    height = 1000  # justerat

    num_shots = 30
    num_goals = random.randint(4, 6)
    shot_or_goal_list = ["goal"] * num_goals + ["shot"] * (num_shots - num_goals)
    random.shuffle(shot_or_goal_list)

    for shot_or_goal in shot_or_goal_list:
        x = random.randint(50, width - 50)
        y = random.randint(50, height - 50)

        phase = random.choice(phases)
        situation = random.choice(situations)
        shot_type = random.choice(shot_types)
        passer = random.choice(hands)
        shooter = random.choice(hands)
        period = random.choice(periods)

        # 💡 30% chans till passpunkt
        if random.random() < 0.3:
            pass_x = x - random.randint(20, 100)
            pass_y = y - random.randint(20, 100)
        else:
            pass_x = pass_y = None

        if shot_or_goal == "goal":
            app.add_goal_event(x, y, phase, situation, shot_type, passer, shooter, period, pass_x, pass_y)
        else:
            app.add_shot_event(x, y, phase, situation, shot_type, passer, shooter, period, pass_x, pass_y)

    print(f"✅ Finished generating {num_shots} demo shots for match: {current_match}")
    app.period_selected.set("All")
    app.update_stats_filtered()
    app.update_shot_log_treeview()
    app.update_plot()
    app.update_stats()
    show_temporary_message(app, "✅ Demo shots generated!")
