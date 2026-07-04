import random

from gui.messages import show_temporary_message

DEMO_PHASES = [
    "Full Court press", "Zone entry defense", "Zone Defense",
    "Zone Exit", "Counter on counter", "Uncontrolled"
]
DEMO_SITUATIONS = [
    "Breakaway", "2v0", "2v1", "3v1", "3v2",
    "Rebound", "Penalty Shot", "Free shot"
]
DEMO_SHOT_TYPES = [
    "One-timer", "Controlled shot", "Own Goal",
    "Deke", "Deflection"
]
DEMO_HANDS = ["Left", "Right"]
DEMO_PERIODS = ["1", "2", "3", "OT"]
DEMO_FIELD_WIDTH = 1455
DEMO_FIELD_HEIGHT = 1000
DEMO_SHOT_COUNT = 30
DEMO_PASS_POINT_CHANCE = 0.3
DEMO_GOAL_MIN = 4
DEMO_GOAL_MAX = 6
DEMO_EDGE_MARGIN = 50
DEMO_PASS_OFFSET_MIN = 20
DEMO_PASS_OFFSET_MAX = 100
DEMO_RESULT_GOAL = "goal"
DEMO_RESULT_SHOT = "shot"


def _can_generate_demo_shots(app) -> bool:
    if app.view_mode.get() == "Plot":
        return True

    print("⛔ Cannot generate demo shots outside of Plot view mode.")
    show_temporary_message(app, "⛔ Switch to 'Plot' mode to add demo shots.")
    return False


def _random_pass_point(x, y):
    if random.random() >= DEMO_PASS_POINT_CHANCE:
        return None, None

    pass_x = x - random.randint(DEMO_PASS_OFFSET_MIN, DEMO_PASS_OFFSET_MAX)
    pass_y = y - random.randint(DEMO_PASS_OFFSET_MIN, DEMO_PASS_OFFSET_MAX)
    return pass_x, pass_y


def _random_point():
    x = random.randint(DEMO_EDGE_MARGIN, DEMO_FIELD_WIDTH - DEMO_EDGE_MARGIN)
    y = random.randint(DEMO_EDGE_MARGIN, DEMO_FIELD_HEIGHT - DEMO_EDGE_MARGIN)
    return x, y


def _random_demo_event():
    x, y = _random_point()
    pass_x, pass_y = _random_pass_point(x, y)

    return {
        "x": x,
        "y": y,
        "phase": random.choice(DEMO_PHASES),
        "situation": random.choice(DEMO_SITUATIONS),
        "shot_type": random.choice(DEMO_SHOT_TYPES),
        "passer": random.choice(DEMO_HANDS),
        "shooter": random.choice(DEMO_HANDS),
        "period": random.choice(DEMO_PERIODS),
        "pass_x": pass_x,
        "pass_y": pass_y,
    }


def _demo_results():
    num_goals = random.randint(DEMO_GOAL_MIN, DEMO_GOAL_MAX)
    results = [DEMO_RESULT_GOAL] * num_goals + [DEMO_RESULT_SHOT] * (DEMO_SHOT_COUNT - num_goals)
    random.shuffle(results)
    return results


def _add_demo_event(app, result: str, event: dict) -> None:
    add_event = app.add_goal_event if result == DEMO_RESULT_GOAL else app.add_shot_event
    add_event(
        event["x"],
        event["y"],
        event["phase"],
        event["situation"],
        event["shot_type"],
        event["passer"],
        event["shooter"],
        event["period"],
        event["pass_x"],
        event["pass_y"],
    )


def _refresh_after_demo_generation(app) -> None:
    app.period_selected.set("All")
    app.update_stats_filtered()
    app.update_shot_log_treeview()
    app.update_plot()
    app.update_stats()


def generate_demo_shots(app):
    if not _can_generate_demo_shots(app):
        return

    print("🔁 Generating demo shots...")

    current_match = app.current_match.get()

    for result in _demo_results():
        _add_demo_event(app, result, _random_demo_event())

    print(f"✅ Finished generating {DEMO_SHOT_COUNT} demo shots for match: {current_match}")
    _refresh_after_demo_generation(app)
    show_temporary_message(app, "✅ Demo shots generated!")
