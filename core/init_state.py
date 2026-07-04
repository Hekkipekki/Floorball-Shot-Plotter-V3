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


def init_variables(self) -> None:
    # === GUI state ===
    self.log_entries = []
    self.view_mode = tk.StringVar(value=DEFAULT_VIEW_MODE)
    self.sensitivity = tk.DoubleVar(value=DEFAULT_SENSITIVITY)
    self.kde_bandwidth = tk.DoubleVar(value=DEFAULT_KDE_BANDWIDTH)
    self.cmap = tk.StringVar(value=DEFAULT_COLORMAP)
    self.period_selected = tk.StringVar(value=DEFAULT_PERIOD)
    self.stats_period = tk.StringVar(value=DEFAULT_PERIOD)
    self.current_match = tk.StringVar(value=DEFAULT_PERIOD)
    self.selected_background = tk.StringVar(value=DEFAULT_BACKGROUND)
    self.bg_choice = tk.StringVar()
    self.resolution_preset = tk.StringVar(value=DEFAULT_RESOLUTION_PRESET)
    self.resolution_options = RESOLUTION_OPTIONS.copy()

    # === Plot / Zoom settings ===
    self.original_xlim = DEFAULT_XLIM
    self.original_ylim = DEFAULT_YLIM
    self.zoom_level = DEFAULT_ZOOM_LEVEL
    self.min_zoom = MIN_ZOOM
    self.max_zoom = MAX_ZOOM

    # === Match data ===
    self.match_logs = {DEFAULT_MATCH: []}
    self.current_match.set(DEFAULT_MATCH)

    # === Internal UI/plot state ===
    self.highlight_artist = None
    self.bg_files = []
