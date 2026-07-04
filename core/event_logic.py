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

SHOT_RESULT = "S"
GOAL_RESULT = "G"
GOAL_XG_VALUE = 1.0


def prepare_event_coordinates(x, y, pass_x, pass_y):
    x = int(round(x))
    y = int(round(y))

    if pass_x is not None:
        pass_x = int(round(pass_x))
    if pass_y is not None:
        pass_y = int(round(pass_y))

    return x, y, pass_x, pass_y


def _current_match_logs(app):
    match = app.current_match.get()
    return app.match_logs.setdefault(match, [])


def _build_event_entry(
    logs,
    result,
    phase,
    situation,
    shot_type,
    passer,
    shooter,
    period,
    xg,
    x,
    y,
    pass_x,
    pass_y,
):
    entry = [None] * ENTRY_LENGTH
    entry[IDX_NUMBER] = len(logs) + 1
    entry[IDX_RESULT] = result
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
    return tuple(entry)


def _add_event(
    app,
    result,
    x,
    y,
    phase,
    situation,
    shot_type,
    passer,
    shooter,
    period,
    pass_x,
    pass_y,
):
    logs = _current_match_logs(app)
    period = period or app.period_selected.get()
    x, y, pass_x, pass_y = prepare_event_coordinates(x, y, pass_x, pass_y)

    xg = (
        get_xg_value(x, y, shot_type, situation, shooter)
        if result == SHOT_RESULT
        else GOAL_XG_VALUE
    )

    logs.append(
        _build_event_entry(
            logs,
            result,
            phase,
            situation,
            shot_type,
            passer,
            shooter,
            period,
            xg,
            x,
            y,
            pass_x,
            pass_y,
        )
    )


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
    _add_event(
        app,
        SHOT_RESULT,
        x,
        y,
        phase,
        situation,
        shot_type,
        passer,
        shooter,
        period,
        pass_x,
        pass_y,
    )


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
    _add_event(
        app,
        GOAL_RESULT,
        x,
        y,
        phase,
        situation,
        shot_type,
        passer,
        shooter,
        period,
        pass_x,
        pass_y,
    )
