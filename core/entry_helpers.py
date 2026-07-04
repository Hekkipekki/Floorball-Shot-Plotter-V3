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


def _get_field(entry, index):
    return normalize_entry(entry)[index]


def _float_or_default(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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
