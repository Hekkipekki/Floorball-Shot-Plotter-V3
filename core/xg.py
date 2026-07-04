import math

DEFAULT_XG = 0.02
XG_ZONES = [
    ((550, 965), (600, 820), 0.3),
    ((550, 965), (355, 599), 0.18),
    ((550, 965), (250, 354), 0.04),
    ((965, 1160), (355, 760), 0.12),
    ((1159, 1315), (355, 760), 0.09),
    ((1314, 1500), (355, 760), 0.05),
    ((345, 550), (355, 760), 0.12),
    ((200, 344), (355, 760), 0.09),
    ((0, 199), (355, 760), 0.05),
    ((200, 0), (0, 249), 0.04),
]
SHOT_TYPE_MULTIPLIERS = {
    "breakaway": 1.5,
    "rebound": 1.2,
    "penalty": 1.8,
    "2v1": 1.4,
}
PHASE_MULTIPLIERS = {
    "set defense": 0.85,
    "zone entry": 1.10,
    "turnover": 1.25,
}


def _in_range(value, bounds):
    start, end = bounds
    return start <= value <= end


def _base_xg_for_position(x, y):
    for x_bounds, y_bounds, value in XG_ZONES:
        if _in_range(x, x_bounds) and _in_range(y, y_bounds):
            return value
    return DEFAULT_XG


def _apply_shot_type_multiplier(xg_value, shot_type):
    return xg_value * SHOT_TYPE_MULTIPLIERS.get(shot_type, 1)


def _apply_stick_hand_multiplier(xg_value, x, stick_hand):
    if stick_hand is None:
        return xg_value

    left_side = x <= 500
    right_side = x >= 1000
    hand = stick_hand.lower()

    if left_side and hand == "right":
        return xg_value * 1.15
    if left_side and hand == "left":
        return xg_value * 0.85
    if right_side and hand == "left":
        return xg_value * 1.15
    if right_side and hand == "right":
        return xg_value * 0.85

    return xg_value


def _apply_phase_multiplier(xg_value, defense_phase):
    if defense_phase is None:
        return xg_value

    phase = defense_phase.lower()
    return xg_value * PHASE_MULTIPLIERS.get(phase, 1)


def get_xg_value(x, y, shot_type, defense_phase=None, stick_hand=None):
    goal_x, goal_y = 0, 0
    distance = math.sqrt((x - goal_x)**2 + (y - goal_y)**2)

    xg_value = _base_xg_for_position(x, y)
    xg_value = _apply_shot_type_multiplier(xg_value, shot_type)
    xg_value = _apply_stick_hand_multiplier(xg_value, x, stick_hand)
    xg_value = _apply_phase_multiplier(xg_value, defense_phase)

    return round(xg_value, 3)
