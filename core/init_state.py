import tkinter as tk

DEFAULT_VIEW_MODE = "Plot"
DEFAULT_SENSITIVITY = 0.2
DEFAULT_KDE_BANDWIDTH = 0.2
DEFAULT_COLORMAP = "jet"
DEFAULT_PERIOD = "All"
DEFAULT_MATCH = "New Match"
DEFAULT_BACKGROUND = "Dark Mode.png"
DEFAULT_RESOLUTION_PRESET = "Medium"

RESOLUTION_OPTIONS = {
    "Low": 300,
    "Medium": 600,
    "High": 800,
    "Ultra": 1200,
}

DEFAULT_XLIM = (0, 1500)
DEFAULT_YLIM = (1000, 0)
DEFAULT_ZOOM_LEVEL = 1.0
MIN_ZOOM = 1.0
MAX_ZOOM = 5.0


def _init_gui_vars(app) -> None:
    app.log_entries = []
    app.view_mode = tk.StringVar(value=DEFAULT_VIEW_MODE)
    app.sensitivity = tk.DoubleVar(value=DEFAULT_SENSITIVITY)
    app.kde_bandwidth = tk.DoubleVar(value=DEFAULT_KDE_BANDWIDTH)
    app.cmap = tk.StringVar(value=DEFAULT_COLORMAP)
    app.period_selected = tk.StringVar(value=DEFAULT_PERIOD)
    app.stats_period = tk.StringVar(value=DEFAULT_PERIOD)
    app.current_match = tk.StringVar(value=DEFAULT_PERIOD)
    app.selected_background = tk.StringVar(value=DEFAULT_BACKGROUND)
    app.bg_choice = tk.StringVar()
    app.resolution_preset = tk.StringVar(value=DEFAULT_RESOLUTION_PRESET)
    app.resolution_options = RESOLUTION_OPTIONS.copy()


def _init_plot_state(app) -> None:
    app.original_xlim = DEFAULT_XLIM
    app.original_ylim = DEFAULT_YLIM
    app.zoom_level = DEFAULT_ZOOM_LEVEL
    app.min_zoom = MIN_ZOOM
    app.max_zoom = MAX_ZOOM


def _init_match_state(app) -> None:
    app.match_logs = {DEFAULT_MATCH: []}
    app.current_match.set(DEFAULT_MATCH)


def _init_internal_state(app) -> None:
    app.highlight_artist = None
    app.bg_files = []


def init_variables(self) -> None:
    _init_gui_vars(self)
    _init_plot_state(self)
    _init_match_state(self)
    _init_internal_state(self)
