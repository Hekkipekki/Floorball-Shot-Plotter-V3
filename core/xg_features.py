from __future__ import annotations

import math

GOAL_CENTER_X = 750
GOAL_CENTER_Y = 1000
GOAL_WIDTH = 160
GOAL_LEFT_X = GOAL_CENTER_X - GOAL_WIDTH / 2
GOAL_RIGHT_X = GOAL_CENTER_X + GOAL_WIDTH / 2

HIGH_DANGER_DISTANCE = 250
MEDIUM_DANGER_DISTANCE = 500
LEFT_ZONE_MAX_X = 500
RIGHT_ZONE_MIN_X = 1000


def _float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def distance_to_goal(x, y) -> float | None:
    x = _float_or_none(x)
    y = _float_or_none(y)
    if x is None or y is None:
        return None

    return round(math.hypot(x - GOAL_CENTER_X, y - GOAL_CENTER_Y), 2)


def shot_angle_to_goal(x, y) -> float | None:
    x = _float_or_none(x)
    y = _float_or_none(y)
    if x is None or y is None:
        return None

    left_angle = math.atan2(GOAL_LEFT_X - x, GOAL_CENTER_Y - y)
    right_angle = math.atan2(GOAL_RIGHT_X - x, GOAL_CENTER_Y - y)
    angle = abs(math.degrees(right_angle - left_angle))

    if angle > 180:
        angle = 360 - angle

    return round(angle, 2)


def shot_zone(x, y) -> str:
    distance = distance_to_goal(x, y)
    x = _float_or_none(x)

    if distance is None or x is None:
        return ""

    if distance <= HIGH_DANGER_DISTANCE:
        danger = "High"
    elif distance <= MEDIUM_DANGER_DISTANCE:
        danger = "Medium"
    else:
        danger = "Low"

    if x < LEFT_ZONE_MAX_X:
        side = "Left"
    elif x > RIGHT_ZONE_MIN_X:
        side = "Right"
    else:
        side = "Center"

    return f"{danger} {side}"


def build_location_features(x, y) -> tuple[float | None, float | None, str]:
    return distance_to_goal(x, y), shot_angle_to_goal(x, y), shot_zone(x, y)
