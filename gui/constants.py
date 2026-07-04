from __future__ import annotations

# ---------------------------------------------------------
# Theme
# ---------------------------------------------------------
DEFAULT_THEME = "darkly"
APP_FONT_FAMILY = "Segoe UI"
APP_FONT_SIZE = 10
APP_FONT_SIZE_SMALL = 9
APP_FONT_SIZE_LARGE = 11
APP_FONT_SIZE_TITLE = 12

# ---------------------------------------------------------
# Layout sizing
# ---------------------------------------------------------
LEFT_PANEL_WIDTH = 310
RIGHT_PANEL_WIDTH = 460

# ---------------------------------------------------------
# Shared spacing
# ---------------------------------------------------------
PAD_X = 7
PAD_Y = 7
SECTION_PAD_X = 6
SECTION_PAD_Y = (7, 0)
BOTTOM_SECTION_PAD_Y = (7, 12)

# ---------------------------------------------------------
# Common widget sizing
# ---------------------------------------------------------
STANDARD_BUTTON_WIDTH = 25
ENTRY_SMALL_WIDTH = 4
PRESET_DESCRIPTION_WRAP = 220

# ---------------------------------------------------------
# Plot defaults
# ---------------------------------------------------------
DEFAULT_CANVAS_WIDTH = 1500
DEFAULT_CANVAS_HEIGHT = 1000

# ---------------------------------------------------------
# Figure / canvas defaults
# ---------------------------------------------------------
FIGURE_WIDTH = 14.5
FIGURE_HEIGHT = 10.5
FIGURE_SUBPLOT_LEFT = 0.05
FIGURE_SUBPLOT_RIGHT = 0.95
FIGURE_SUBPLOT_TOP = 0.95
FIGURE_SUBPLOT_BOTTOM = 0.05

# ---------------------------------------------------------
# Shot log sizing
# ---------------------------------------------------------
SHOTLOG_FONT_FAMILY = "Segoe UI Emoji"
SHOTLOG_FONT_SIZE = 10
SHOTLOG_ROW_HEIGHT = 26
SHOTLOG_HEADING_FONT_SIZE = 10

SHOTLOG_VIDEO_ICON_SIZE = 16
SHOTLOG_VIDEO_ICON_BG = (44, 62, 80, 255)

SHOTLOG_COL_WIDTH_NUMBER = 32
SHOTLOG_COL_WIDTH_RESULT = 42

SHOTLOG_COL_WIDTH_PHASE = 95
SHOTLOG_COL_WIDTH_SITUATION = 82
SHOTLOG_COL_WIDTH_TYPE = 105

SHOTLOG_COL_WIDTH_PASSER = 52
SHOTLOG_COL_WIDTH_SHOOTER = 78

SHOTLOG_COL_WIDTH_PERIOD = 36
SHOTLOG_COL_WIDTH_XG = 52
SHOTLOG_COL_WIDTH_VIDEO = 48

# ---------------------------------------------------------
# Plot styling
# ---------------------------------------------------------
PLOT_DEFAULT_XLIM = (0, 1500)
PLOT_DEFAULT_YLIM = (1000, 0)

PASS_ARROW_OFFSET = 15
PASS_ARROW_COLOR = "red"
PASS_ARROW_LINEWIDTH = 2
PASS_ARROW_MUTATION_SCALE = 15
PASS_ARROW_ZORDER = 8

HIGHLIGHT_GOAL_SIZE = 70
HIGHLIGHT_GOAL_FACE = "red"
HIGHLIGHT_GOAL_EDGE = "black"
HIGHLIGHT_GOAL_LINEWIDTH = 1

HIGHLIGHT_SHOT_SIZE = 120
HIGHLIGHT_SHOT_EDGE = "yellow"
HIGHLIGHT_SHOT_FACE = "none"
HIGHLIGHT_SHOT_LINEWIDTH = 2

HIGHLIGHT_PASS_SIZE = 50
HIGHLIGHT_PASS_FACE = "cyan"
HIGHLIGHT_PASS_EDGE = "black"
HIGHLIGHT_PASS_LINEWIDTH = 1

HIGHLIGHT_SHOOTER_TEXT_COLOR = "yellow"
HIGHLIGHT_PASSER_TEXT_COLOR = "cyan"
HIGHLIGHT_TEXT_FONT_SIZE = 10
HIGHLIGHT_TEXT_X_OFFSET = 12
HIGHLIGHT_TEXT_Y_OFFSET = -12
HIGHLIGHT_TEXT_BBOX_FC = "black"
HIGHLIGHT_TEXT_BBOX_ALPHA = 0.75
HIGHLIGHT_SHOOTER_BBOX_EC = "yellow"
HIGHLIGHT_PASSER_BBOX_EC = "cyan"

HOVER_DISTANCE_THRESHOLD_PX = 15
# ---------------------------------------------------------
# Standard plot point styling
# ---------------------------------------------------------
PLOT_POINT_EDGE_COLOR = "black"
PLOT_POINT_EDGE_WIDTH = 0.5

PLOT_SHOT_SIZE = 60
PLOT_GOAL_SIZE = 70
PLOT_SHOT_ZORDER = 5
PLOT_GOAL_ZORDER = 6
PLOT_GOAL_COLOR = "red"
PLOT_FALLBACK_SHOT_COLOR = "gray"
PLOT_FALLBACK_SHOT_LABEL = "Other"

PLOT_SHOT_TYPE_STYLES = {
    "One-timer": ("blue", "One-timer"),
    "Controlled shot": ("orange", "Controlled shot"),
    "Own Goal": ("black", "Own Goal"),
    "Deke": ("purple", "Deke"),
    "Deflection": ("green", "Deflection"),
}

# ---------------------------------------------------------
# Plot legend styling
# ---------------------------------------------------------
PLOT_LEGEND_LOC = "lower right"
PLOT_LEGEND_BBOX = (1.055, -0.055)
PLOT_LEGEND_FRAME_ON = True
PLOT_LEGEND_FACE_COLOR = "white"
PLOT_LEGEND_EDGE_COLOR = "black"
PLOT_LEGEND_FONT_SIZE = 10
PLOT_LEGEND_LABEL_SPACING = 0.4
PLOT_LEGEND_HANDLE_LENGTH = 1.8
PLOT_LEGEND_BORDER_PAD = 0.7
PLOT_LEGEND_BORDER_AXES_PAD = 0.4
PLOT_LEGEND_FRAME_ALPHA = 1.0

# ---------------------------------------------------------
# Future xG-based marker scaling
# ---------------------------------------------------------
PLOT_USE_XG_SCALING = False
PLOT_XG_MIN_SIZE = 35
PLOT_XG_MAX_SIZE = 140
PLOT_XG_FALLBACK_SIZE = PLOT_SHOT_SIZE
