import ttkbootstrap as tb

from gui.panels.controls.period_controls import (
    setup_period_controls,
    setup_view_mode_controls,
)
from gui.panels.controls.stats_controls import (
    setup_expected_goals_controls,
    setup_stats_filter_controls,
)
from gui.panels.controls.heatmap_controls import (
    setup_heatmap_settings_group,
)
from gui.panels.controls.match_controls import (
    setup_demo_shots_button,
    setup_match_management,
)


def setup_controls(parent: tb.Frame, app) -> None:
    setup_period_controls(app, parent)
    setup_view_mode_controls(app, parent)
    setup_stats_filter_controls(app, parent)
    setup_expected_goals_controls(app, parent)
    setup_heatmap_settings_group(app, parent)
    setup_match_management(app, parent)
    setup_demo_shots_button(app, parent)