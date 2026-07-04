from core.filtering import (
    get_filtered_entries,
    get_filtered_entries_by_period,
)
from core.event_logic import (
    add_shot_event as create_shot_event,
    add_goal_event as create_goal_event,
)
from core.schema import IDX_RESULT, IDX_XG

SHOT_RESULT = "S"
GOAL_RESULT = "G"
COUNTED_RESULTS = (SHOT_RESULT, GOAL_RESULT)

HEATMAP_PRESETS = {
    "Match Analysis": (0.17, 0.16),
    "Multi-Match": (0.23, 0.22),
    "Season Review": (0.30, 0.25),
    "Season Review (Goal only)": (0.23, 0.22),
}
DEFAULT_HEATMAP_PRESET = (0.20, 0.20)

HEATMAP_PRESET_DESCRIPTIONS = {
    "Match Analysis": "Well-rounded smoothing, includes most shots.",
    "Multi-Match": "Balanced: shows main clusters.",
    "Season Review": "Focused: dense zones only.",
    "Season Review (Goal only)": "Goal-focused overview.",
}


class CoreLogic:
    def __init__(self, app):
        self.app = app

    # ---------------------------------------------------------
    # Filtering (public)
    # ---------------------------------------------------------
    def get_filtered_entries(self):
        return get_filtered_entries(self.app)

    def get_filtered_entries_by_period(self, period_filter):
        return get_filtered_entries_by_period(self.app, period_filter)

    # ---------------------------------------------------------
    # Stats
    # ---------------------------------------------------------
    def update_stats(self, filtered_entries=None):
        if filtered_entries is None:
            stats_period = self.app.stats_period.get()
            entries = self.get_filtered_entries_by_period(stats_period)
        else:
            entries = filtered_entries

        total = len([e for e in entries if e[IDX_RESULT] in COUNTED_RESULTS])
        goals = len([e for e in entries if e[IDX_RESULT] == GOAL_RESULT])
        saves = total - goals
        pct = (saves / total) * 100 if total > 0 else 0

        self.app.totalshots_val.config(text=str(total))
        self.app.shots_val.config(text=str(saves))
        self.app.goals_val.config(text=str(goals))
        self.app.savepct_val.config(text=f"{pct:.2f}%")

    def update_expected_goals(self):
        entries = self.get_filtered_entries_by_period(
            self.app.stats_period.get()
        )

        xg_sum = sum(e[IDX_XG] for e in entries if e[IDX_RESULT] == SHOT_RESULT)
        goals = sum(1 for e in entries if e[IDX_RESULT] == GOAL_RESULT)

        if hasattr(self.app, "xg_goals_val"):
            self.app.xg_goals_val.config(text=f"{xg_sum:.2f}")

        if hasattr(self.app, "actual_goals_val"):
            self.app.actual_goals_val.config(text=str(goals))

    # ---------------------------------------------------------
    # Event creation
    # ---------------------------------------------------------
    def add_shot_event(
        self,
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
        create_shot_event(
            self.app,
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
        self,
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
        create_goal_event(
            self.app,
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

    # ---------------------------------------------------------
    # Heatmap presets
    # ---------------------------------------------------------
    def apply_heatmap_preset(self):
        preset = self.app.heatmap_preset.get()
        kde, sens = HEATMAP_PRESETS.get(preset, DEFAULT_HEATMAP_PRESET)

        self.app.kde_bandwidth.set(kde)
        self.app.sensitivity.set(sens)

        if hasattr(self.app, "sens_entry"):
            self.app.sens_entry.delete(0, "end")
            self.app.sens_entry.insert(0, f"{sens:.2f}")

        if hasattr(self.app, "kde_entry"):
            self.app.kde_entry.delete(0, "end")
            self.app.kde_entry.insert(0, f"{kde:.2f}")

        self.app.update_plot()

    def update_preset_description(self):
        if not hasattr(self.app, "preset_description"):
            return

        preset = self.app.heatmap_preset.get()
        self.app.preset_description.config(
            text=HEATMAP_PRESET_DESCRIPTIONS.get(preset, "")
        )
