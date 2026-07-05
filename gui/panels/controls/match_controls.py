import ttkbootstrap as tb

from gui.constants import PAD_X, PAD_Y, SECTION_PAD_X, BOTTOM_SECTION_PAD_Y, STANDARD_BUTTON_WIDTH
from utils.tooltips import BetterToolTip

MATCH_MANAGER_BUTTONS = (
    ("➕ New Match", "start_new_match", (PAD_Y, 3), None, "primary", "Start logging a new empty match without removing loaded matches."),
    ("📂 Load Match...", "handle_load_match", (0, 3), None, "secondary", "Choose from existing matches to load."),
    ("📁 Load Several Matches", "handle_load_season", (0, 3), None, "secondary", "Load all matches or grouped folders."),
    ("🗑 Delete This Match", "delete_current_match", (0, 3), None, "secondary", "Remove the currently selected match."),
    ("💾 Save as...", "prompt_save_match", (0, PAD_Y), None, "secondary", "Save the current shots/goals as a new match."),
)
MATCH_MANAGER_STYLE = "secondary"
DEMO_STYLE = "secondary"
DEMO_BUTTON_STYLE = "secondary"


def _create_full_width_button(parent: tb.Frame, text: str, command, pady, image=None, style="secondary") -> tb.Button:
    button_options = {
        "text": text,
        "command": command,
        "bootstyle": style,
        "width": STANDARD_BUTTON_WIDTH,
    }

    if image is not None:
        button_options["image"] = image
        button_options["compound"] = "left"

    button = tb.Button(parent, **button_options)
    button.pack(fill="x", padx=PAD_X, pady=pady)
    return button


def _button_image(app, image_attr):
    if image_attr is None:
        return None
    return getattr(app, image_attr, None)


def _add_match_manager_button(app, frame, text, command_attr, pady, image_attr, style, tooltip):
    button = _create_full_width_button(
        frame,
        text=text,
        command=getattr(app, command_attr),
        pady=pady,
        image=_button_image(app, image_attr),
        style=style,
    )
    BetterToolTip(button, tooltip)
    return button


def setup_match_management(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Match Manager", bootstyle=MATCH_MANAGER_STYLE)
    frame.pack(fill="x", pady=BOTTOM_SECTION_PAD_Y, padx=SECTION_PAD_X)

    for text, command_attr, pady, image_attr, style, tooltip in MATCH_MANAGER_BUTTONS:
        button = _add_match_manager_button(app, frame, text, command_attr, pady, image_attr, style, tooltip)
        if command_attr == "delete_current_match":
            app.delete_match_btn = button


def setup_demo_shots_button(app, parent: tb.Frame) -> None:
    frame = tb.Labelframe(parent, text="Demo Data", bootstyle=DEMO_STYLE)
    frame.pack(fill="x", pady=BOTTOM_SECTION_PAD_Y, padx=SECTION_PAD_X)

    demo_btn = _create_full_width_button(
        frame,
        text="✨ Generate Demo Shots",
        command=app.generate_demo_shots,
        pady=PAD_Y,
        style=DEMO_BUTTON_STYLE,
    )

    BetterToolTip(demo_btn, "Generate example shots and goals for testing and experimentation.")
