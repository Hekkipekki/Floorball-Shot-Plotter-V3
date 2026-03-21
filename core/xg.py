import math

def get_xg_value(x, y, shot_type, defense_phase=None, stick_hand=None):
    goal_x, goal_y = 0, 0
    distance = math.sqrt((x - goal_x)**2 + (y - goal_y)**2)

    if 550 <= x <= 965 and 600 <= y <= 820:
        xg_value = 0.3
    elif 550 <= x <= 965 and 355 <= y < 600:
        xg_value = 0.18
    elif 550 <= x <= 965 and 250 <= y <= 354:
        xg_value = 0.04
    elif 965 <= x <= 1160 and 355 <= y <= 760:
        xg_value = 0.12
    elif 1159 <= x <= 1315 and 355 <= y <= 760:
        xg_value = 0.09
    elif 1314 <= x <= 1500 and 355 <= y <= 760:
        xg_value = 0.05
    elif 345 <= x <= 550 and 355 <= y <= 760:
        xg_value = 0.12
    elif 200 <= x <= 344 and 355 <= y <= 760:
        xg_value = 0.09
    elif 0 <= x <= 199 and 355 <= y <= 760:
        xg_value = 0.05
    elif 200 <= x <= 0 and 0 <= y <= 249:
        xg_value = 0.04
    else:
        xg_value = 0.02

    shot_type_multipliers = {
        "breakaway": 1.5,
        "rebound": 1.2,
        "penalty": 1.8,
        "2v1": 1.4
    }
    xg_value *= shot_type_multipliers.get(shot_type, 1)

    if stick_hand is not None:
        left_side = x <= 500
        right_side = x >= 1000
        if left_side and stick_hand.lower() == "right":
            xg_value *= 1.15
        elif left_side and stick_hand.lower() == "left":
            xg_value *= 0.85
        elif right_side and stick_hand.lower() == "left":
            xg_value *= 1.15
        elif right_side and stick_hand.lower() == "right":
            xg_value *= 0.85

    if defense_phase is not None:
        phase = defense_phase.lower()
        if phase == "set defense":
            xg_value *= 0.85
        elif phase == "zone entry":
            xg_value *= 1.10
        elif phase == "turnover":
            xg_value *= 1.25

    return round(xg_value, 3)