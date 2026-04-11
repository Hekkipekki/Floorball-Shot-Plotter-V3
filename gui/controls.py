import ttkbootstrap as tb
import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
from utils.tooltips import BetterToolTip

# -----------------------------
# 📌 PERIOD- OCH VIEW-KONTROLLER
# -----------------------------
def setup_period_controls(self, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Period", bootstyle="primary")
    frame.pack(fill="x", expand=False, pady=(5, 0), padx=3)
    BetterToolTip(frame, "Select if you want to log shots/goals to a specific period.")

    button_frame = tb.Frame(frame)
    button_frame.pack(fill="x", padx=5, pady=(3, 3))

    period_buttons = ["1", "2", "3", "OT", "All"]
    tooltip_texts = {
        "1": "Select to log events to Period 1.",
        "2": "Select to log events to Period 2.",
        "3": "Select to log events to Period 3.",
        "OT": "Select to log events to Overtime.",
        "All": "Show events from all periods."
    }
    self.period_buttons = {}

    for period in period_buttons:
        btn_width = 4 if period == "All" else 3 if period == "OT" else 2
        button = tb.Button(
            button_frame,
            text=period,
            command=lambda p=period: self.set_period_filter(p),
            width=btn_width,
            bootstyle="primary"
        )
        button.pack(side="left", padx=3, pady=(2, 4))
        BetterToolTip(button, tooltip_texts[period])
        self.period_buttons[period] = button

    self.period_selected.trace("w", lambda *args: self.update_period_button_styles())


def setup_view_mode_controls(self, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="View Mode", bootstyle="primary")
    frame.pack(fill="x", pady=(5, 0), padx=3)

    view_options = ["Plot", "Heatmap", "Goal Heatmap", "Save Heatmap"]
    self.view_mode.set("Plot")

    def on_select(event=None):
        selected = self.view_mode_dropdown.get()
        self.view_mode.set(selected)
        self.update_plot()

    self.view_mode_dropdown = ttk.Combobox(
        frame,
        values=view_options,
        textvariable=self.view_mode,
        state="readonly",
        bootstyle="info"
    )
    self.view_mode_dropdown.pack(fill="x", padx=5)
    self.view_mode_dropdown.bind("<<ComboboxSelected>>", on_select)
    BetterToolTip(self.view_mode_dropdown,
        "Change the visualization mode:\n"
        "- Plot = regular shot plot\n"
        "- Heatmaps = density views of shots or goals"
    )


# -----------------------------
# 📈 STATISTIK OCH XG-VISNING
# -----------------------------
def setup_stats_filter_controls(self, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Statistics", bootstyle="primary")
    frame.pack(fill="x", pady=(5, 0), padx=3)
    stats = tb.Frame(frame)
    stats.pack(anchor="center", padx=5, pady=(5, 0))
    stats.grid_columnconfigure(0, weight=1)
    stats.grid_columnconfigure(1, weight=1)

    def label_row(row, text, var_attr):
        label = tb.Label(stats, text=text, font=("Segoe UI", 10))
        label.grid(row=row, column=0, sticky="w", padx=(5, 0), pady=2)
        value = tb.Label(stats, text="0", anchor="w", font=("Segoe UI", 11))
        value.grid(row=row, column=1, sticky="w", padx=(10, 0), pady=2)
        setattr(self, var_attr, value)

    label_row(0, "Shots (Saved):", "shots_val")
    label_row(1, "Goals Conceded:", "goals_val")
    label_row(2, "Total Shots:", "totalshots_val")
    label_row(3, "Save %:", "savepct_val")

    tb.Separator(frame, orient="horizontal").pack(fill="x", pady=(6, 3))
    row = tb.Frame(frame)
    row.pack(anchor="w", padx=5, pady=(0, 5), fill="x")
    row.grid_columnconfigure(0, weight=1)
    row.grid_columnconfigure(1, weight=1)

    tb.Label(row, text="Filter by Period:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w")
    period_options = ["All", "1", "2", "3", "OT"]
    self.stats_period_dropdown = ttk.Combobox(
        row,
        textvariable=self.stats_period,
        values=period_options,
        state="readonly",
        width=9,
        bootstyle="info"
    )
    self.stats_period_dropdown.grid(row=0, column=1, sticky="e")
    self.stats_period_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_stats_filtered())


def setup_expected_goals_controls(self, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Expected Goals", bootstyle="primary")
    frame.pack(fill="x", pady=(5, 0), padx=3)

    stats = tb.Frame(frame)
    stats.pack(anchor="center", padx=5, pady=(5, 5))
    stats.grid_columnconfigure(0, weight=1)
    stats.grid_columnconfigure(1, weight=1)

    tooltip = "Expected Goals (xG): how many goals should have been conceded based on shot quality."

    label_xg = tb.Label(stats, text="xG Goals:", font=("Segoe UI", 11))
    label_xg.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=1)
    self.xg_goals_val = tb.Label(stats, text="0.00", anchor="w", font=("Segoe UI", 11))
    self.xg_goals_val.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=1)

    label_goals = tb.Label(stats, text="Goals:", font=("Segoe UI", 11))
    label_goals.grid(row=1, column=0, sticky="w", padx=(5, 0), pady=1)
    self.actual_goals_val = tb.Label(stats, text="0", anchor="w", font=("Segoe UI", 11))
    self.actual_goals_val.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=1)

    for w in [frame, label_xg, self.xg_goals_val, label_goals, self.actual_goals_val]:
        BetterToolTip(w, tooltip)


# -----------------------------
# 🎨 HEATMAP- OCH KÄNSLIGHET
# -----------------------------
def setup_heatmap_settings_group(self, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Heatmap Settings", bootstyle="primary")
    frame.pack(fill="x", pady=(3, 0), padx=3)

    # 🎨 Color selection
    tb.Label(frame, text="Select heatmap color:", font=("Segoe UI", 10)).pack(padx=5, pady=(2, 1), anchor="w")
    self.colormap_combobox = ttk.Combobox(
        frame,
        values=["inferno", "plasma", "magma", "hot", "jet"],
        textvariable=self.cmap,
        state="readonly",
        bootstyle="primary"
    )
    self.colormap_combobox.pack(fill="x", padx=5, pady=(0, 2))
    self.colormap_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_plot())

    # 📐 Quality
    tb.Label(frame, text="Heatmap Quality:", font=("Segoe UI", 10)).pack(padx=5, pady=(1, 1), anchor="w")
    self.resolution_combobox = ttk.Combobox(
        frame,
        values=list(self.resolution_options.keys()),
        textvariable=self.resolution_preset,
        state="readonly",
        bootstyle="primary"
    )
    self.resolution_combobox.pack(fill="x", padx=5, pady=(0, 2))
    self.resolution_combobox.bind("<<ComboboxSelected>>", lambda e: self.update_plot())

    # 🧠 Presets
    tb.Label(frame, text="Preset:", font=("Segoe UI", 10)).pack(padx=5, pady=(1, 1), anchor="w")
    self.heatmap_preset = tk.StringVar(value="Match Analysis")
    self.heatmap_preset_dropdown = ttk.Combobox(
        frame,
        values=[
            "Match Analysis", "Multi-Match", "Season Review", "Season Review (Goal only)"
        ],
        textvariable=self.heatmap_preset,
        state="readonly",
        bootstyle="primary"
    )
    self.heatmap_preset_dropdown.pack(fill="x", padx=5, pady=(0, 2))
    self.heatmap_preset_dropdown.bind("<<ComboboxSelected>>", lambda e: self.on_preset_changed())

    self.preset_description = tb.Label(
        frame,
        text="",
        font=("Segoe UI", 8, "italic"),
        wraplength=220,              # Anpassa bredden efter behov
        justify="left"
    )
    self.preset_description.pack(padx=5, pady=(0, 5), anchor="w")

    # 🎚 Sensitivity
    tb.Label(frame, text="Sensitivity:", font=("Segoe UI", 10)).pack(padx=5, pady=(1, 1), anchor="w")
    self.sens_slider = tb.Scale(
        frame, from_=0.01, to=1.0, orient="horizontal",
        variable=self.sensitivity, length=110,
        command=lambda val: self.apply_sensitivity(from_slider=True)
    )
    self.sens_slider.pack(fill="x", padx=5)
    self.sens_entry = tb.Entry(frame, width=4)
    self.sens_entry.insert(0, f"{self.sensitivity.get():.2f}")
    self.sens_entry.pack(padx=5, pady=(0, 2), anchor="e")
    self.sens_entry.bind("<Return>", lambda e: self.apply_sensitivity(from_slider=False))

    # 🎚 KDE Bandwidth
    tb.Label(frame, text="KDE Bandwidth:", font=("Segoe UI", 10)).pack(padx=5, pady=(1, 1), anchor="w")
    self.kde_slider = tb.Scale(
        frame, from_=0.01, to=1.0, orient="horizontal",
        variable=self.kde_bandwidth, length=110,
        command=lambda val: self.apply_kde(from_slider=True)
    )
    self.kde_slider.pack(fill="x", padx=5)
    self.kde_entry = tb.Entry(frame, width=4)
    self.kde_entry.insert(0, f"{self.kde_bandwidth.get():.2f}")
    self.kde_entry.pack(padx=5, pady=(0, 2), anchor="e")
    self.kde_entry.bind("<Return>", lambda e: self.apply_kde(from_slider=False))


# -----------------------------
# 📁 MATCHHANTERING OCH DEMO
# -----------------------------
def setup_match_management(self, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Match Manager", bootstyle="primary")
    frame.pack(fill="x", pady=(5, 10), padx=3)

    # 🔄 Load Match
    load_btn = tb.Button(
        frame,
        text="Load Match...",
        command=self.handle_load_match,
        bootstyle="primary",
        width=25
    )
    load_btn.pack(fill="x", padx=5, pady=(5, 3))

    # 🔁 Load Season
    season_btn = tb.Button(
        frame,
        text="Load Several Matches",
        command=self.handle_load_season,
        bootstyle="primary",
        width=25
    )
    season_btn.pack(fill="x", padx=5, pady=(0, 3))

    # ❌ Delete Match
    self.delete_match_btn = tb.Button(
        frame,
        text="Delete This Match",
        command=self.delete_current_match,
        bootstyle="primary",
        width=25
    )
    self.delete_match_btn.pack(fill="x", padx=5, pady=(0, 3))

    # 💾 Save
    save_btn = tb.Button(
        frame,
        text="Save as....",
        command=self.prompt_save_match,
        bootstyle="primary",
        width=25
    )
    save_btn.pack(fill="x", padx=5, pady=(0, 5))

    # Tooltips (valfritt)
    BetterToolTip(load_btn, "Choose from existing matches to load.")
    BetterToolTip(season_btn, "Load all matches or grouped folders.")
    BetterToolTip(self.delete_match_btn, "Remove the currently selected match.")
    BetterToolTip(save_btn, "Save the current shots/goals as a new match.")

def setup_demo_shots_button(self, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Demo Data", bootstyle="primary")
    frame.pack(fill="x", pady=(5, 10), padx=3)

    demo_btn = tb.Button(
        frame,
        text="Generate Demo Shots",
        command=self.generate_demo_shots,
        bootstyle="primary",
        width=25
    )
    demo_btn.pack(fill="x", padx=5, pady=5)

    BetterToolTip(demo_btn, "Generate example shots and goals for testing and experimentation.")
