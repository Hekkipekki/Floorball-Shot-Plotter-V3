# Entry tuple/list schema indexes.
# Keep existing indexes stable for JSON/CSV compatibility.
# New model-training fields must be appended at the end.

IDX_NUMBER = 0
IDX_RESULT = 1
IDX_PHASE = 2
IDX_SITUATION = 3
IDX_TYPE = 4
IDX_PASSER = 5
IDX_SHOOTER = 6
IDX_PERIOD = 7
IDX_XG = 8
IDX_X = 9
IDX_Y = 10
IDX_PASS_X = 11
IDX_PASS_Y = 12
IDX_VIDEO = 13
IDX_DISTANCE = 14
IDX_ANGLE = 15
IDX_ZONE = 16
IDX_STRENGTH_STATE = 17
IDX_CHANCE_TYPE = 18
IDX_SCREEN = 19
IDX_PRESSURE = 20
IDX_GOALIE_STATE = 21
IDX_PERIOD_TIME = 22

ENTRY_LENGTH = 23

ENTRY_FIELD_NAMES = (
    "number",
    "result",
    "phase",
    "situation",
    "type",
    "passer",
    "shooter",
    "period",
    "xg",
    "x",
    "y",
    "pass_x",
    "pass_y",
    "video",
    "distance",
    "angle",
    "zone",
    "strength_state",
    "chance_type",
    "screen",
    "pressure",
    "goalie_state",
    "period_time",
)
