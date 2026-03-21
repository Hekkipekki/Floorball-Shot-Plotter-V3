class CoreLogic:
    """
    Core logic for:
    - filtering entries
    - calculating stats
    - calculating expected goals display values
    - applying heatmap presets
    - coordinating refresh of log/plot/stats

    Event creation should NOT live here anymore.
    That belongs in the event/service layer.
    """

    def __init__(self, app):
        self.app = app

    # ---------------------------------------------------------
    # Filtering
    # ---------------------------------------------------------
    def get_filtered_entries(self):
        """
        Returns entries for the currently selected match and plot period filter.
        """
        match = self.app.current_match.get()
        period = self.app.period_selected.get()
        return self._filter_entries(match, period)

    def get_filtered_entries_by_period(self, period_filter):
        """
        Returns entries for the currently selected match and a supplied period filter.
        Used mainly for stats/xG calculations.
        """
        match = self.app.current_match.get()
        return self._filter_entries(match, period_filter)

    def _filter_entries(self, match, period):
        """
        Internal shared filter logic.
        Entry structure:
            0  #,
            1  S/G,
            2  Phase,
            3  Situation,
            4  Type,
            5  Passer,
            6  Shooter,
            7  Period,
            8  xG,
            9  X,
            10 Y,
            11 Pass X,
            12 Pass Y,
            13 Video
        """
        if match == "All":
            entries = []
            for logs in self.app.match_logs.values():
                entries.extend(logs)
        else:
            entries = list(self.app.match_logs.get(match, []))

        if period != "All":
            entries = [entry for entry in entries if str(entry[7]) == str(period)]

        return entries

    # ---------------------------------------------------------
    # Stats
    # ---------------------------------------------------------
    def update_stats(self, filtered_entries=None):
        """
        Updates the stat labels in the UI.
        If no filtered_entries are provided, stats use the stats period filter.
        """
        if filtered_entries is None:
            stats_period = self.app.stats_period.get()
            entries = self.get_filtered_entries_by_period(stats_period)
        else:
            entries = filtered_entries

        total = len([entry for entry in entries if entry[1] in ("S", "G")])
        goals = len([entry for entry in entries if entry[1] == "G"])
        saves = total - goals
        save_pct = (saves / total) * 100 if total > 0 else 0.0

        self.app.totalshots_val.config(text=str(total))
        self.app.shots_val.config(text=str(saves))
        self.app.goals_val.config(text=str(goals))
        self.app.savepct_val.config(text=f"{save_pct:.2f}%")

    def update_expected_goals(self):
        """
        Updates xG goals and actual goals labels based on the stats period filter.
        """
        stats_entries = self.get_filtered_entries_by_period(self.app.stats_period.get())

        xg_sum = sum(entry[8] for entry in stats_entries if entry[1] == "S")
        num_goals = sum(1 for entry in stats_entries if entry[1] == "G")

        if hasattr(self.app, "xg_goals_val"):
            self.app.xg_goals_val.config(text=f"{xg_sum:.2f}")

        if hasattr(self.app, "actual_goals_val"):
            self.app.actual_goals_val.config(text=str(num_goals))

    # ---------------------------------------------------------
    # Heatmap presets
    # ---------------------------------------------------------
    def apply_heatmap_preset(self):
        """
        Applies preset KDE/sensitivity values from the selected heatmap preset.
        """
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
        """
        Updates the descriptive helper text for the selected heatmap preset.
        """
        if not hasattr(self.app, "preset_description"):
            return

        descriptions = {
            "Match Analysis": "Well-rounded smoothing, includes most shots.",
            "Multi-Match": "Balanced: shows main clusters, filters light noise.",
            "Season Review": "Focused: only dense, recurring shot zones remain.",
            "Season Review (Goal only)": "Goal-focused overview for entire season (~50-60 goals).",
        }

        preset = self.app.heatmap_preset.get()
        text = descriptions.get(preset, "")
        self.app.preset_description.config(text=text)

    # ---------------------------------------------------------
    # Refresh orchestration
    # ---------------------------------------------------------
    def update_log_view_and_stats(self):
        """
        Refreshes:
        - visible log entries
        - shot log treeview
        - plot
        - stats
        - expected goals
        """
        filtered_entries = self.get_filtered_entries()
        self.app.log_entries = filtered_entries

        self.app.update_shot_log_treeview()
        self.app.update_plot()

        stats_entries = self.get_filtered_entries_by_period(self.app.stats_period.get())
        self.update_stats(stats_entries)
        self.update_expected_goals()