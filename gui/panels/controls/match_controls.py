import ttkbootstrap as tb

from gui.constants import PAD_X, PAD_Y, SECTION_PAD_X, BOTTOM_SECTION_PAD_Y, STANDARD_BUTTON_WIDTH
from utils.tooltips import BetterToolTip


def _create_full_width_button(parent: tb.Frame, text: str, command, pady) -> tb.Button:
    button = tb.Button(
        parent,
        text=text,
        command=command,
        bootstyle="primary",
        width=STANDARD_BUTTON_WIDTH,
    )
    button.pack(fill="x", padx=PAD_X, pady=pady)
    return button


def setup_match_management(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Match Manager", bootstyle="primary")
    frame.pack(fill="x", pady=BOTTOM_SECTION_PAD_Y, padx=SECTION_PAD_X)

    load_btn = _create_full_width_button(
        frame,
        text="Load Match...",
        command=app.handle_load_match,
        pady=(PAD_Y, 3),
    )

    season_btn = _create_full_width_button(
        frame,
        text="Load Several Matches",
        command=app.handle_load_season,
        pady=(0, 3),
    )

    app.delete_match_btn = _create_full_width_button(
        frame,
        text="Delete This Match",
        command=app.delete_current_match,
        pady=(0, 3),
    )

    save_btn = _create_full_width_button(
        frame,
        text="Save as....",
        command=app.prompt_save_match,
        pady=(0, PAD_Y),
    )

    BetterToolTip(load_btn, "Choose from existing matches to load.")
    BetterToolTip(season_btn, "Load all matches or grouped folders.")
    BetterToolTip(app.delete_match_btn, "Remove the currently selected match.")
    BetterToolTip(save_btn, "Save the current shots/goals as a new match.")


def setup_demo_shots_button(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Demo Data", bootstyle="primary")
    frame.pack(fill="x", pady=BOTTOM_SECTION_PAD_Y, padx=SECTION_PAD_X)

    demo_btn = _create_full_width_button(
        frame,
        text="Generate Demo Shots",
        command=app.generate_demo_shots,
        pady=PAD_Y,
    )

    BetterToolTip(demo_btn, "Generate example shots and goals for testing and experimentation.")
