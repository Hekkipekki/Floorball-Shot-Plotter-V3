from core.xg import get_xg_value
from core.xg_context import infer_xg_context_defaults, normalize_xg_context
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
    IDX_STRENGTH_STATE,
    IDX_CHANCE_TYPE,
    IDX_SCREEN,
    IDX_PRESSURE,
    IDX_GOALIE_STATE,
    IDX_PERIOD_TIME,
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


def _normalized_context(phase, situation, shot_type, context):
    inferred = infer_xg_context_defaults(phase, situation, shot_type)
    if isinstance(context, dict):
        inferred.update({key: value for key, value in context.items() if value not in (None, "")})
    return normalize_xg_context(inferred)


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
    context,
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
    entry[IDX_STRENGTH_STATE] = context["strength_state"]
    entry[IDX_CHANCE_TYPE] = context["chance_type"]
    entry[IDX_SCREEN] = context["screen"]
    entry[IDX_PRESSURE] = context["pressure"]
    entry[IDX_GOALIE_STATE] = context["goalie_state"]
    entry[IDX_PERIOD_TIME] = context["period_time"]
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
    context=None,
):
    logs = _current_match_logs(app)
    period = period or app.period_selected.get()
    x, y, pass_x, pass_y = prepare_event_coordinates(x, y, pass_x, pass_y)
    context = _normalized_context(phase, situation, shot_type, context)

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
            context,
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
    context=None,
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
        context,
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
    context=None,
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
        context,
    )
