from core.xg import get_xg_value

class CoreLogic:
    def __init__(self, app):
        self.app = app

    def update_stats(self, filtered_entries=None):
        if filtered_entries is None:
            stats_period = self.app.stats_period.get()
            entries = self.get_filtered_entries_by_period(stats_period)
        else:
            entries = filtered_entries

        total = len([e for e in entries if e[1] in ["S", "G"]])
        goals = len([e for e in entries if e[1] == "G"])
        saves = total - goals
        pct = (saves / total) * 100 if total > 0 else 0.0

        self.app.totalshots_val.config(text=str(total))
        self.app.shots_val.config(text=str(saves))
        self.app.goals_val.config(text=str(goals))
        self.app.savepct_val.config(text=f"{pct:.2f}%")

    def update_expected_goals(self):
        stats_entries = self.get_filtered_entries_by_period(self.app.stats_period.get())
        xg_sum = sum(entry[8] for entry in stats_entries if entry[1] == "S")
        num_goals = sum(1 for entry in stats_entries if entry[1] == "G")

        if hasattr(self.app, "xg_goals_val") and hasattr(self.app, "actual_goals_val"):
            self.app.xg_goals_val.config(text=f"{xg_sum:.2f}")
            self.app.actual_goals_val.config(text=str(num_goals))

    def get_filtered_entries(self):
        match = self.app.current_match.get()
        period = self.app.period_selected.get()
        return self._filter_entries(match, period)

    def get_filtered_entries_by_period(self, period_filter):
        match = self.app.current_match.get()
        return self._filter_entries(match, period_filter)

    def _filter_entries(self, match, period):
        if match == "All":
            entries = []
            for logs in self.app.match_logs.values():
                entries.extend(logs)
        else:
            entries = self.app.match_logs.get(match, [])

        if period != "All":
            entries = [e for e in entries if str(e[7]) == str(period)]  # e[7] = period

        return entries

    def add_shot_event(self, x, y, phase, situation, shot_type, passer, shooter, period=None, pass_x=None, pass_y=None):
        period = period or self.app.period_selected.get()
        x, y = int(round(x)), int(round(y))
        xg = get_xg_value(x, y, shot_type, situation, shooter)

        entry = (
            len(self.app.match_logs[self.app.current_match.get()]) + 1,  # #
            "S",                # S/G
            phase,              # Phase
            situation,          # Situation
            shot_type,          # Type
            passer,             # Passer
            shooter,            # Shooter
            period,             # Period
            xg,                 # xG
            x, y,               # X, Y
            pass_x, pass_y      # Pass X, Y
        )

        self.app.match_logs[self.app.current_match.get()].append(entry)

    def add_goal_event(self, x, y, phase, situation, shot_type, passer, shooter, period=None, pass_x=None, pass_y=None):
        period = period or self.app.period_selected.get()
        x, y = int(round(x)), int(round(y))
        xg = 1.0  # Full xG för mål

        entry = (
            len(self.app.match_logs[self.app.current_match.get()]) + 1,
            "G",
            phase,
            situation,
            shot_type,
            passer,
            shooter,
            period,
            xg,
            x, y,
            pass_x, pass_y
        )

        self.app.match_logs[self.app.current_match.get()].append(entry)

    def apply_heatmap_preset(self):
        preset = self.app.heatmap_preset.get()
        presets = {
            "Match Analysis": (0.17, 0.16),
            "Multi-Match": (0.23, 0.22),
            "Season Review": (0.30, 0.25),
            "Season Review (Goal only)": (0.23, 0.22),
        }
        kde, sens = presets.get(preset, (0.2, 0.2))
        self.app.kde_bandwidth.set(kde)
        self.app.sensitivity.set(sens)

        if hasattr(self.app, 'sens_entry'):
            self.app.sens_entry.delete(0, "end")
            self.app.sens_entry.insert(0, f"{sens:.2f}")
        if hasattr(self.app, 'kde_entry'):
            self.app.kde_entry.delete(0, "end")
            self.app.kde_entry.insert(0, f"{kde:.2f}")

        self.app.update_plot()

    def update_preset_description(self):
        if not hasattr(self.app, "preset_description"):
            return

        descriptions = {
            "Match Analysis": "Well-rounded smoothing, includes most shots.",
            "Multi-Match": "Balanced: shows main clusters, filters light noise.",
            "Season Review": "Focused: only dense, recurring shot zones remain.",
            "Season Review (Goal only)": "Goal-focused overview for entire season (~50-60 goals)."
        }

        preset = self.app.heatmap_preset.get()
        text = descriptions.get(preset, "")
        self.app.preset_description.config(text=text)

    def update_log_view_and_stats(self):
        filtered_entries = self.get_filtered_entries()
        self.app.log_entries = filtered_entries
        self.app.update_shot_log_treeview()
        self.app.update_plot()

        stats_entries = self.get_filtered_entries_by_period(self.app.stats_period.get())
        self.update_stats(stats_entries)
        self.update_expected_goals()
