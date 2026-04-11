import tkinter as tk


def init_variables(self) -> None:
    # === GUI state ===
    self.log_entries = []
    self.view_mode = tk.StringVar(value="Plot")
    self.sensitivity = tk.DoubleVar(value=0.2)
    self.kde_bandwidth = tk.DoubleVar(value=0.2)
    self.cmap = tk.StringVar(value="jet")
    self.period_selected = tk.StringVar(value="All")
    self.stats_period = tk.StringVar(value="All")
    self.current_match = tk.StringVar(value="All")
    self.selected_background = tk.StringVar(value="Dark Mode.png")
    self.bg_choice = tk.StringVar()
    self.resolution_preset = tk.StringVar(value="Medium")
    self.resolution_options = {
        "Low": 300,
        "Medium": 600,
        "High": 800,
        "Ultra": 1200,
    }

    # === Plot / Zoom settings ===
    self.original_xlim = (0, 1500)
    self.original_ylim = (1000, 0)
    self.zoom_level = 1.0
    self.min_zoom = 1.0
    self.max_zoom = 5.0

    # === Match data ===
    self.match_logs = {"New Match": []}
    self.current_match.set("New Match")

    # === Internal UI/plot state ===
    self.highlight_artist = None
    self.bg_files = []