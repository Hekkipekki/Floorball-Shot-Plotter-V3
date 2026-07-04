import ttkbootstrap as tb

from gui.panels.controls.period_controls import (
    setup_period_controls,
    setup_view_mode_controls,
)
from gui.panels.controls.stats_controls import (
    setup_expected_goals_controls,
    setup_stats_filter_controls,
)
from gui.panels.controls.match_controls import (
    setup_demo_shots_button,
    setup_match_management,
)

CONTROL_SETUP_STEPS = (
    setup_period_controls,
    setup_view_mode_controls,
    setup_stats_filter_controls,
    setup_expected_goals_controls,
    setup_match_management,
    setup_demo_shots_button,
)


def setup_controls(parent: tb.Frame, app) -> None:
    for setup_step in CONTROL_SETUP_STEPS:
        setup_step(app, parent)
