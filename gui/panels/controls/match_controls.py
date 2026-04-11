import ttkbootstrap as tb

from gui.constants import PAD_X, PAD_Y, SECTION_PAD_X, BOTTOM_SECTION_PAD_Y, STANDARD_BUTTON_WIDTH
from utils.tooltips import BetterToolTip


def setup_match_management(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Match Manager", bootstyle="primary")
    frame.pack(fill="x", pady=BOTTOM_SECTION_PAD_Y, padx=SECTION_PAD_X)

    load_btn = tb.Button(
        frame,
        text="Load Match...",
        command=app.handle_load_match,
        bootstyle="primary",
        width=STANDARD_BUTTON_WIDTH,
    )
    load_btn.pack(fill="x", padx=PAD_X, pady=(PAD_Y, 3))

    season_btn = tb.Button(
        frame,
        text="Load Several Matches",
        command=app.handle_load_season,
        bootstyle="primary",
        width=STANDARD_BUTTON_WIDTH,
    )
    season_btn.pack(fill="x", padx=PAD_X, pady=(0, 3))

    app.delete_match_btn = tb.Button(
        frame,
        text="Delete This Match",
        command=app.delete_current_match,
        bootstyle="primary",
        width=STANDARD_BUTTON_WIDTH,
    )
    app.delete_match_btn.pack(fill="x", padx=PAD_X, pady=(0, 3))

    save_btn = tb.Button(
        frame,
        text="Save as....",
        command=app.prompt_save_match,
        bootstyle="primary",
        width=STANDARD_BUTTON_WIDTH,
    )
    save_btn.pack(fill="x", padx=PAD_X, pady=(0, PAD_Y))

    BetterToolTip(load_btn, "Choose from existing matches to load.")
    BetterToolTip(season_btn, "Load all matches or grouped folders.")
    BetterToolTip(app.delete_match_btn, "Remove the currently selected match.")
    BetterToolTip(save_btn, "Save the current shots/goals as a new match.")


def setup_demo_shots_button(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Demo Data", bootstyle="primary")
    frame.pack(fill="x", pady=BOTTOM_SECTION_PAD_Y, padx=SECTION_PAD_X)

    demo_btn = tb.Button(
        frame,
        text="Generate Demo Shots",
        command=app.generate_demo_shots,
        bootstyle="primary",
        width=STANDARD_BUTTON_WIDTH,
    )
    demo_btn.pack(fill="x", padx=PAD_X, pady=PAD_Y)

    BetterToolTip(demo_btn, "Generate example shots and goals for testing and experimentation.")