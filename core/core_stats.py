from core.xg import get_xg_value


class CoreLogic:
    def __init__(self, app):
        self.app = app

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------
    def _get_match_entries(self, match):
        if match == "All":
            entries = []
            for logs in self.app.match_logs.values():
                entries.extend(logs)
            return entries
        return self.app.match_logs.get(match, [])

    def _filter_by_period(self, entries, period):
        if period == "All":
            return entries
        return [e for e in entries if str(e[7]) == str(period)]

    # ---------------------------------------------------------
    # Filtering (public)
    # ---------------------------------------------------------
    def get_filtered_entries(self):
        match = self.app.current_match.get()
        period = self.app.period_selected.get()

        entries = self._get_match_entries(match)
        return self._filter_by_period(entries, period)

    def get_filtered_entries_by_period(self, period_filter):
        match = self.app.current_match.get()

        entries = self._get_match_entries(match)
        return self._filter_by_period(entries, period_filter)

    # ---------------------------------------------------------
    # Stats
    # ---------------------------------------------------------
    def update_stats(self, filtered_entries=None):
        if filtered_entries is None:
            stats_period = self.app.stats_period.get()
            entries = self.get_filtered_entries_by_period(stats_period)
        else:
            entries = filtered_entries

        total = len([e for e in entries if e[1] in ("S", "G")])
        goals = len([e for e in entries if e[1] == "G"])
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

        xg_sum = sum(e[8] for e in entries if e[1] == "S")
        goals = sum(1 for e in entries if e[1] == "G")

        if hasattr(self.app, "xg_goals_val"):
            self.app.xg_goals_val.config(text=f"{xg_sum:.2f}")

        if hasattr(self.app, "actual_goals_val"):
            self.app.actual_goals_val.config(text=str(goals))

    # ---------------------------------------------------------
    # Event creation
    # ---------------------------------------------------------
    def _prepare_event(self, x, y, pass_x, pass_y):
        x = int(round(x))
        y = int(round(y))

        if pass_x is not None:
            pass_x = int(round(pass_x))
        if pass_y is not None:
            pass_y = int(round(pass_y))

        return x, y, pass_x, pass_y

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
        match = self.app.current_match.get()
        logs = self.app.match_logs.setdefault(match, [])

        period = period or self.app.period_selected.get()
        x, y, pass_x, pass_y = self._prepare_event(x, y, pass_x, pass_y)

        xg = get_xg_value(x, y, shot_type, situation, shooter)

        entry = (
            len(logs) + 1,
            "S",
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

        logs.append(entry)

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
        match = self.app.current_match.get()
        logs = self.app.match_logs.setdefault(match, [])

        period = period or self.app.period_selected.get()
        x, y, pass_x, pass_y = self._prepare_event(x, y, pass_x, pass_y)

        entry = (
            len(logs) + 1,
            "G",
            phase,
            situation,
            shot_type,
            passer,
            shooter,
            period,
            1.0,
            x,
            y,
            pass_x,
            pass_y,
        )

        logs.append(entry)

    # ---------------------------------------------------------
    # Heatmap presets
    # ---------------------------------------------------------
    def apply_heatmap_preset(self):
        preset = self.app.heatmap_preset.get()

        presets = {
            "Match Analysis": (0.17, 0.16),
            "Multi-Match": (0.23, 0.22),
            "Season Review": (0.30, 0.25),
            "Season Review (Goal only)": (0.23, 0.22),
        }

        kde, sens = presets.get(preset, (0.20, 0.20))

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

        descriptions = {
            "Match Analysis": "Well-rounded smoothing, includes most shots.",
            "Multi-Match": "Balanced: shows main clusters.",
            "Season Review": "Focused: dense zones only.",
            "Season Review (Goal only)": "Goal-focused overview.",
        }

        preset = self.app.heatmap_preset.get()
        self.app.preset_description.config(text=descriptions.get(preset, ""))

    # ---------------------------------------------------------
    # Refresh
    # ---------------------------------------------------------
    def update_log_view_and_stats(self):
        filtered_entries = self.get_filtered_entries()

        self.app.log_entries = filtered_entries
        self.app.update_shot_log_treeview()
        self.app.update_plot()

        stats_entries = self.get_filtered_entries_by_period(
            self.app.stats_period.get()
        )

        self.update_stats(stats_entries)
        self.update_expected_goals()