from core.xg import get_xg_value
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
    ENTRY_LENGTH,
)


def prepare_event_coordinates(x, y, pass_x, pass_y):
    x = int(round(x))
    y = int(round(y))

    if pass_x is not None:
        pass_x = int(round(pass_x))
    if pass_y is not None:
        pass_y = int(round(pass_y))

    return x, y, pass_x, pass_y


def add_shot_event(
    app,
    x,
    y,
    phase,
    situation,
    shot_type,
    passer,
    shooter,
    period=None,
    pass_x=None,
    pass_y=None,
):
    match = app.current_match.get()
    logs = app.match_logs.setdefault(match, [])

    period = period or app.period_selected.get()
    x, y, pass_x, pass_y = prepare_event_coordinates(x, y, pass_x, pass_y)

    xg = get_xg_value(x, y, shot_type, situation, shooter)

    entry = [None] * ENTRY_LENGTH
    entry[IDX_NUMBER] = len(logs) + 1
    entry[IDX_RESULT] = "S"
    entry[IDX_PHASE] = phase
    entry[IDX_SITUATION] = situation
    entry[IDX_TYPE] = shot_type
    entry[IDX_PASSER] = passer
    entry[IDX_SHOOTER] = shooter
    entry[IDX_PERIOD] = period
    entry[IDX_XG] = xg
    entry[IDX_X] = x
    entry[IDX_Y] = y
    entry[IDX_PASS_X] = pass_x
    entry[IDX_PASS_Y] = pass_y

    logs.append(tuple(entry))


def add_goal_event(
    app,
    x,
    y,
    phase,
    situation,
    shot_type,
    passer,
    shooter,
    period=None,
    pass_x=None,
    pass_y=None,
):
    match = app.current_match.get()
    logs = app.match_logs.setdefault(match, [])

    period = period or app.period_selected.get()
    x, y, pass_x, pass_y = prepare_event_coordinates(x, y, pass_x, pass_y)

    entry = [None] * ENTRY_LENGTH
    entry[IDX_NUMBER] = len(logs) + 1
    entry[IDX_RESULT] = "G"
    entry[IDX_PHASE] = phase
    entry[IDX_SITUATION] = situation
    entry[IDX_TYPE] = shot_type
    entry[IDX_PASSER] = passer
    entry[IDX_SHOOTER] = shooter
    entry[IDX_PERIOD] = period
    entry[IDX_XG] = 1.0
    entry[IDX_X] = x
    entry[IDX_Y] = y
    entry[IDX_PASS_X] = pass_x
    entry[IDX_PASS_Y] = pass_y

    logs.append(tuple(entry))