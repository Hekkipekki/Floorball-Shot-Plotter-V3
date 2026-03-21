# ui/tooltips.py
import tkinter as tk
from tkinter import font as tkfont
import ttkbootstrap as tb

class BetterToolTip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self._after_id = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.on_motion)

    def schedule(self, event=None):
        self.unschedule()
        self._after_id = self.widget.after(self.delay, self.show_tooltip)

    def unschedule(self):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.widget.winfo_ismapped():
            return

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        tooltip_width = 250
        screen_width = self.widget.winfo_screenwidth()

        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg="#333333")

        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#333333",
            foreground="#ffffff",
            relief="flat",
            borderwidth=0,
            font=tkfont.Font(family="Segoe UI", size=9),
            wraplength=tooltip_width,
            padx=10,
            pady=5
        )
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        self.unschedule()
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def on_motion(self, event):
        self.schedule()

def update_preset_tooltip(app):
    if not hasattr(app, "heatmap_preset_dropdown"):
        return

    descriptions = {
        "Match Analysis": (
            "🎯 For single games (20–30 shots)\n"
            "🧠 Shows most shot areas\n"
            "📈 High detail, minimal filtering"
        ),
        "Multi-Match": (
            "🎯 For 3–5 games (60–100 shots or goals)\n"
            "🧠 Balanced smoothing and filtering\n"
            "📈 Highlights dominant areas"
        ),
        "Season Review": (
            "🎯 For season overview (200+ shots or goals)\n"
            "🧠 Filters out rare zones\n"
            "📈 Only persistent patterns remain"
        ),
        "Season Review (Goal only)": (
            "🎯 Goal heatmap for full season (~50–60 goals)\n"
            "📈 Only clustered goal areas remain"
        )
    }

    selected = app.heatmap_preset.get()
    tooltip_text = descriptions.get(selected, "Select a preset to configure heatmap settings.")
    BetterToolTip(app.heatmap_preset_dropdown, tooltip_text)

def add_tooltips(app):
    if hasattr(app, "period_buttons"):
        for period, btn in app.period_buttons.items():
            BetterToolTip(btn, f"Filter to show only period {period} data.")

    if hasattr(app, "view_mode_dropdown"):
        BetterToolTip(app.view_mode_dropdown,
            "Change the visualization mode:\n"
            "- Plot = regular shot plot\n"
            "- Heatmaps = density views of shots or goals"
        )

    if hasattr(app, "stats_period_dropdown"):
        BetterToolTip(app.stats_period_dropdown, "Filter the statistics and shot log by period.")

    if hasattr(app, "colormap_combobox"):
        BetterToolTip(app.colormap_combobox, "Choose a colormap for the heatmap (e.g., inferno, plasma, jet).")

    if hasattr(app, "resolution_combobox"):
        BetterToolTip(app.resolution_combobox,
            "Set heatmap resolution.\n"
            "Low = faster rendering\n"
            "Ultra = highly detailed."
        )

    if hasattr(app, "heatmap_preset_dropdown"):
        BetterToolTip(app.heatmap_preset_dropdown,
            "Select preset KDE + Sensitivity values:\n"
            "- Match Analysis = precise, local detail\n"
            "- Season Review = dense zones only"
        )

    if hasattr(app, "sens_slider"):
        BetterToolTip(app.sens_slider,
            "Sensitivity:\n"
            "- Low = more areas visible\n"
            "- High = only dense zones visible\n\n"
            "Controls how many shots are needed\n"
            "in an area for it to appear on the heatmap."
        )

    if hasattr(app, "sens_entry"):
        BetterToolTip(app.sens_entry,
            "Manually enter a sensitivity value (0.01 – 1.0).\n"
            "Higher values filter out weak zones."
        )

    if hasattr(app, "kde_slider"):
        BetterToolTip(app.kde_slider,
            "KDE Bandwidth:\n"
            "- Low = more detailed and sharp zones\n"
            "- High = broader, blended zones\n\n"
            "Controls how far each shot influences nearby space."
        )

    if hasattr(app, "kde_entry"):
        BetterToolTip(app.kde_entry,
            "Manually enter KDE bandwidth (0.01 – 1.0).\n"
            "Higher values smooth more, lower values are sharper."
        )

    if hasattr(app, "generate_demo_shots"):
        try:
            for child in app.left_panel.winfo_children():
                if isinstance(child, tb.Labelframe) and "Demo Data" in child.cget("text"):
                    for btn in child.winfo_children():
                        if isinstance(btn, tb.Button):
                            BetterToolTip(btn, "Generate example shots and goals for testing.")
        except Exception as e:
            print("Tooltip assignment for demo button failed:", e)
