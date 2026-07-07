from __future__ import annotations

from core.schema import (
    IDX_NUMBER,
    IDX_RESULT,
    IDX_PHASE,
    IDX_SITUATION,
    IDX_TYPE,
    IDX_PASSER,
    IDX_SHOOTER,
    IDX_PERIOD,
    IDX_XG,
    IDX_X,
    IDX_Y,
    IDX_PASS_X,
    IDX_PASS_Y,
    IDX_VIDEO,
    IDX_DISTANCE,
    IDX_ANGLE,
    IDX_ZONE,
    IDX_STRENGTH_STATE,
    IDX_CHANCE_TYPE,
    IDX_SCREEN,
    IDX_PRESSURE,
    IDX_GOALIE_STATE,
    IDX_PERIOD_TIME,
    ENTRY_LENGTH,
)
from core.xg_context import infer_xg_context_defaults
from core.xg_features import build_location_features


def _float_or_default(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _add_missing_location_features(row) -> None:
    x = _float_or_default(row[IDX_X])
    y = _float_or_default(row[IDX_Y])
    if x is None or y is None:
        return

    distance, angle, zone = build_location_features(x, y)

    if row[IDX_DISTANCE] in (None, ""):
        row[IDX_DISTANCE] = distance
    if row[IDX_ANGLE] in (None, ""):
        row[IDX_ANGLE] = angle
    if row[IDX_ZONE] in (None, ""):
        row[IDX_ZONE] = zone


def _add_missing_xg_context(row) -> None:
    defaults = infer_xg_context_defaults(row[IDX_PHASE] or "", row[IDX_SITUATION] or "", row[IDX_TYPE] or "")
    field_map = {
        IDX_STRENGTH_STATE: "strength_state",
        IDX_CHANCE_TYPE: "chance_type",
        IDX_SCREEN: "screen",
        IDX_PRESSURE: "pressure",
        IDX_GOALIE_STATE: "goalie_state",
        IDX_PERIOD_TIME: "period_time",
    }
    for index, key in field_map.items():
        if row[index] in (None, ""):
            row[index] = defaults[key]


def normalize_entry(entry):
    """
    Return a safe list version of an entry padded to the full schema length.
    """
    row = list(entry) if entry is not None else []
    if len(row) < ENTRY_LENGTH:
        row += [None] * (ENTRY_LENGTH - len(row))

    _add_missing_location_features(row)
    _add_missing_xg_context(row)
    return row


def _get_field(entry, index):
    return normalize_entry(entry)[index]


def _get_float_pair(entry, x_index, y_index):
    row = normalize_entry(entry)
    x = _float_or_default(row[x_index])
    y = _float_or_default(row[y_index])

    if x is None or y is None:
        return None, None

    return x, y


def get_number(entry):
    return _get_field(entry, IDX_NUMBER)


def get_result(entry):
    return _get_field(entry, IDX_RESULT)


def get_phase(entry):
    return _get_field(entry, IDX_PHASE)


def get_situation(entry):
    return _get_field(entry, IDX_SITUATION)


def get_type(entry):
    return _get_field(entry, IDX_TYPE)


def get_passer(entry):
    return _get_field(entry, IDX_PASSER)


def get_shooter(entry):
    return _get_field(entry, IDX_SHOOTER)


def get_period(entry):
    return _get_field(entry, IDX_PERIOD)


def get_xg(entry, default=0.0):
    return _float_or_default(_get_field(entry, IDX_XG), default)


def get_xy(entry):
    return _get_float_pair(entry, IDX_X, IDX_Y)


def get_pass_xy(entry):
    return _get_float_pair(entry, IDX_PASS_X, IDX_PASS_Y)


def has_pass_point(entry):
    pass_x, pass_y = get_pass_xy(entry)
    return pass_x is not None and pass_y is not None


def get_video(entry):
    return _get_field(entry, IDX_VIDEO)


def get_distance(entry, default=""):
    return _float_or_default(_get_field(entry, IDX_DISTANCE), default)


def get_angle(entry, default=""):
    return _float_or_default(_get_field(entry, IDX_ANGLE), default)


def get_zone(entry):
    return _get_field(entry, IDX_ZONE) or ""


def get_strength_state(entry):
    return _get_field(entry, IDX_STRENGTH_STATE) or ""


def get_chance_type(entry):
    return _get_field(entry, IDX_CHANCE_TYPE) or ""


def get_screen(entry):
    return _get_field(entry, IDX_SCREEN) or ""


def get_pressure(entry):
    return _get_field(entry, IDX_PRESSURE) or ""


def get_goalie_state(entry):
    return _get_field(entry, IDX_GOALIE_STATE) or ""


def get_period_time(entry):
    return _get_field(entry, IDX_PERIOD_TIME) or ""
