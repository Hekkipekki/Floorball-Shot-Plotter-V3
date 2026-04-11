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
    ENTRY_LENGTH,
)


def normalize_entry(entry):
    """
    Return a safe list version of an entry padded to the full schema length.
    """
    row = list(entry) if entry is not None else []
    if len(row) < ENTRY_LENGTH:
        row += [None] * (ENTRY_LENGTH - len(row))
    return row


def get_number(entry):
    return normalize_entry(entry)[IDX_NUMBER]


def get_result(entry):
    return normalize_entry(entry)[IDX_RESULT]


def get_phase(entry):
    return normalize_entry(entry)[IDX_PHASE]


def get_situation(entry):
    return normalize_entry(entry)[IDX_SITUATION]


def get_type(entry):
    return normalize_entry(entry)[IDX_TYPE]


def get_passer(entry):
    return normalize_entry(entry)[IDX_PASSER]


def get_shooter(entry):
    return normalize_entry(entry)[IDX_SHOOTER]


def get_period(entry):
    return normalize_entry(entry)[IDX_PERIOD]


def get_xg(entry, default=0.0):
    value = normalize_entry(entry)[IDX_XG]
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_xy(entry):
    row = normalize_entry(entry)

    try:
        x = row[IDX_X]
        y = row[IDX_Y]
        if x is None or y is None:
            return None, None
        return float(x), float(y)
    except (TypeError, ValueError):
        return None, None


def get_pass_xy(entry):
    row = normalize_entry(entry)

    try:
        pass_x = row[IDX_PASS_X]
        pass_y = row[IDX_PASS_Y]
        if pass_x is None or pass_y is None:
            return None, None
        return float(pass_x), float(pass_y)
    except (TypeError, ValueError):
        return None, None


def has_pass_point(entry):
    pass_x, pass_y = get_pass_xy(entry)
    return pass_x is not None and pass_y is not None


def get_video(entry):
    return normalize_entry(entry)[IDX_VIDEO]