from __future__ import annotations

import math

# Measured against the current defensive-half background image.
# This keeps distance/angle aligned with the same rink coordinates used by video calibration.
GOAL_CENTER_X = 740
GOAL_CENTER_Y = 990
GOAL_WIDTH = 160
GOAL_LEFT_X = GOAL_CENTER_X - GOAL_WIDTH / 2
GOAL_RIGHT_X = GOAL_CENTER_X + GOAL_WIDTH / 2

# The plotted background is the defending half of an official 40m x 20m rink.
# The distance shown in the shot log is zone depth from the goal line toward the
# centre line, so it is clamped to 0..20m. This avoids diagonal corner distances
# exceeding the defensive-zone length.
RINK_LEFT_X = 18
RINK_RIGHT_X = 1431
RINK_TOP_Y = 20
RINK_GOAL_LINE_Y = GOAL_CENTER_Y
RINK_WIDTH_UNITS = RINK_RIGHT_X - RINK_LEFT_X
RINK_LENGTH_UNITS = RINK_GOAL_LINE_Y - RINK_TOP_Y
DEFENSIVE_ZONE_WIDTH_METERS = 20
DEFENSIVE_ZONE_LENGTH_METERS = 20
METERS_PER_X_UNIT = DEFENSIVE_ZONE_WIDTH_METERS / RINK_WIDTH_UNITS
METERS_PER_Y_UNIT = DEFENSIVE_ZONE_LENGTH_METERS / RINK_LENGTH_UNITS

RINK_WIDTH = 1500
LEFT_THIRD_MAX_X = 500
RIGHT_THIRD_MIN_X = 1000
CENTER_LEFT_X = 500
CENTER_RIGHT_X = 1000
GOAL_AREA_LEFT_X = 620
GOAL_AREA_RIGHT_X = 880
SLOT_LEFT_X = 500
SLOT_RIGHT_X = 1000

END_ZONE_MAX_Y = 300
HIGH_SLOT_MAX_Y = 500
SLOT_SPOT_MAX_Y = 760
GOAL_AREA_MIN_Y = 760
BEHIND_NET_MIN_Y = 900

ZONE_1_BEHIND_NET_LEFT = "1 Behind Net Left"
ZONE_7_BEHIND_NET_RIGHT = "7 Behind Net Right"
ZONE_2_LOWER_LEFT = "2 Lower Left Side"
ZONE_6_LOWER_RIGHT = "6 Lower Right Side"
ZONE_3_ANGLED_LEFT = "3 Angled Shot Left"
ZONE_5_ANGLED_RIGHT = "5 Angled Shot Right"
ZONE_4_1_HIGH_SLOT_LEFT = "4.1 High Slot Left"
ZONE_4_2_HIGH_SLOT_CENTER = "4.2 High Slot Center"
ZONE_4_3_HIGH_SLOT_RIGHT = "4.3 High Slot Right"
ZONE_4_4_HIGH_DANGER_SLOT = "4.4 High Danger Slot Spot"
ZONE_4_5_HIGH_DANGER_GOAL = "4.5 High Danger Goal Area"
ZONE_8_1_END_LEFT = "8.1 Left End Zone"
ZONE_8_2_END_CENTER = "8.2 Center End Zone"
ZONE_8_3_END_RIGHT = "8.3 Right End Zone"


def _float_or_none(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _left_center_right(x, left_label, center_label, right_label):
    if x < LEFT_THIRD_MAX_X:
        return left_label
    if x > RIGHT_THIRD_MIN_X:
        return right_label
    return center_label


def _plot_delta_to_meters(dx, dy) -> tuple[float, float]:
    return dx * METERS_PER_X_UNIT, dy * METERS_PER_Y_UNIT


def _clamp_distance(distance: float) -> float:
    return max(0.0, min(DEFENSIVE_ZONE_LENGTH_METERS, distance))


def distance_to_goal(x, y) -> float | None:
    x = _float_or_none(x)
    y = _float_or_none(y)
    if x is None or y is None:
        return None

    depth_units = RINK_GOAL_LINE_Y - y
    depth_meters = depth_units * METERS_PER_Y_UNIT
    return round(_clamp_distance(depth_meters), 2)


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


def _end_zone(x):
    return _left_center_right(
        x,
        ZONE_8_1_END_LEFT,
        ZONE_8_2_END_CENTER,
        ZONE_8_3_END_RIGHT,
    )


def _high_slot_zone(x):
    return _left_center_right(
        x,
        ZONE_4_1_HIGH_SLOT_LEFT,
        ZONE_4_2_HIGH_SLOT_CENTER,
        ZONE_4_3_HIGH_SLOT_RIGHT,
    )


def _is_goal_area(x, y) -> bool:
    return GOAL_AREA_LEFT_X <= x <= GOAL_AREA_RIGHT_X and y >= GOAL_AREA_MIN_Y


def _is_slot_spot(x, y) -> bool:
    return SLOT_LEFT_X <= x <= SLOT_RIGHT_X and y < SLOT_SPOT_MAX_Y


def _is_left_side(x) -> bool:
    return x < CENTER_LEFT_X


def _is_right_side(x) -> bool:
    return x > CENTER_RIGHT_X


def shot_zone(x, y) -> str:
    x = _float_or_none(x)
    y = _float_or_none(y)

    if x is None or y is None:
        return ""

    if y <= END_ZONE_MAX_Y:
        return _end_zone(x)

    if y <= HIGH_SLOT_MAX_Y:
        return _high_slot_zone(x)

    if _is_goal_area(x, y):
        return ZONE_4_5_HIGH_DANGER_GOAL

    if _is_slot_spot(x, y):
        return ZONE_4_4_HIGH_DANGER_SLOT

    if _is_left_side(x):
        if y >= BEHIND_NET_MIN_Y:
            return ZONE_1_BEHIND_NET_LEFT
        if y >= SLOT_SPOT_MAX_Y:
            return ZONE_2_LOWER_LEFT
        return ZONE_3_ANGLED_LEFT

    if _is_right_side(x):
        if y >= BEHIND_NET_MIN_Y:
            return ZONE_7_BEHIND_NET_RIGHT
        if y >= SLOT_SPOT_MAX_Y:
            return ZONE_6_LOWER_RIGHT
        return ZONE_5_ANGLED_RIGHT

    return ZONE_4_4_HIGH_DANGER_SLOT


def build_location_features(x, y) -> tuple[float | None, float | None, str]:
    return distance_to_goal(x, y), shot_angle_to_goal(x, y), shot_zone(x, y)
