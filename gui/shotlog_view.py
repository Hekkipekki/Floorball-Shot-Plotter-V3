import tkinter as tk
import ttkbootstrap as tb

from core.entry_helpers import (
    get_number,
    get_phase,
    get_result,
    get_situation,
    get_type,
    get_passer,
    get_shooter,
    get_period,
    get_xg,
    get_xy,
    get_distance,
    get_angle,
    get_zone,
    get_video,
)
from gui.constants import (
    PAD_X,
    PAD_Y,
    SHOTLOG_COL_WIDTH_NUMBER,
    SHOTLOG_COL_WIDTH_PASSER,
    SHOTLOG_COL_WIDTH_PERIOD,
    SHOTLOG_COL_WIDTH_PHASE,
    SHOTLOG_COL_WIDTH_RESULT,
    SHOTLOG_COL_WIDTH_SHOOTER,
    SHOTLOG_COL_WIDTH_SITUATION,
    SHOTLOG_COL_WIDTH_TYPE,
    SHOTLOG_COL_WIDTH_VIDEO,
    SHOTLOG_COL_WIDTH_XG,
    SHOTLOG_FONT_FAMILY,
    SHOTLOG_FONT_SIZE,
)
from gui.shotlog_video import video_display_symbol, open_video_menu
from gui.shotlog_interactions import (
    on_hover_shot,
    on_leave_shotlog,
    on_row_double_click,
)

SHOTLOG_COLUMNS = (
    "#",
    "S/G",
    "Phase",
    "Situation",
    "Type",
    "Passer",
    "Shooter",
    "P",
    "xG",
    "X",
    "Y",
    "Distance",
    "Angle",
    "Zone",
    "Video",
)
DEFAULT_VISIBLE_COLUMNS = ("#", "S/G", "Phase", "Situation", "Type", "Passer", "Shooter", "P", "xG", "Video")
SHOTLOG_COLUMN_WIDTHS = {
    "#": SHOTLOG_COL_WIDTH_NUMBER,
    "S/G": SHOTLOG_COL_WIDTH_RESULT,
    "Phase": SHOTLOG_COL_WIDTH_PHASE,
    "Situation": SHOTLOG_COL_WIDTH_SITUATION,
    "Type": SHOTLOG_COL_WIDTH_TYPE,
    "Passer": SHOTLOG_COL_WIDTH_PASSER,
    "Shooter": SHOTLOG_COL_WIDTH_SHOOTER,
    "P": SHOTLOG_COL_WIDTH_PERIOD,
    "xG": SHOTLOG_COL_WIDTH_XG,
    "X": 70,
    "Y": 70,
    "Distance": 90,
    "Angle": 75,
    "Zone": 100,
    "Video": SHOTLOG_COL_WIDTH_VIDEO,
}
SHOTLOG_DEFAULT_COLUMN_WIDTH = 60
TREEVIEW_STYLE_NAME = "Treeview"
VIDEO_COLUMN = "Video"
VIDEO_COLUMN_HEADING = "🎬"
COLUMN_BUTTON_TEXT = "Columns ▾"
COLUMN_POPUP_TITLE = "Shot Log Columns"
COLUMN_POPUP_COLUMNS = 2
COLUMN_POPUP_PAD_X = 10
COLUMN_POPUP_PAD_Y = 4


def _shotlog_heading_text(column: str) -> str:
    return VIDEO_COLUMN_HEADING if column == VIDEO_COLUMN else column


def _configure_shotlog_columns(tree: tb.Treeview) -> None:
    for column in SHOTLOG_COLUMNS:
        tree.heading(column, text=_shotlog_heading_text(column))
        tree.column(
            column,
            anchor="center",
            width=SHOTLOG_COLUMN_WIDTHS.get(column, SHOTLOG_DEFAULT_COLUMN_WIDTH),
            stretch=False,
        )


def _bind_shotlog_events(tree: tb.Treeview, app) -> None:
    event_bindings = (
        ("<Motion>", lambda e: on_hover_shot(e, tree, app)),
        ("<Leave>", lambda e: on_leave_shotlog(e, tree, app)),
        ("<Double-1>", lambda e: on_row_double_click(e, tree, app)),
        ("<Button-3>", lambda e: open_video_menu(e, tree, app)),
    )
    for event_name, callback in event_bindings:
        tree.bind(event_name, callback)


def _format_optional_float(value) -> str:
    if value in (None, ""):
        return ""
    return f"{float(value):.2f}"


def _entry_values(entry) -> list:
    x, y = get_xy(entry)
    return [
        get_number(entry),
        get_result(entry),
        get_phase(entry),
        get_situation(entry),
        get_type(entry),
        get_passer(entry),
        get_shooter(entry),
        get_period(entry),
        f"{get_xg(entry):.2f}",
        _format_optional_float(x),
        _format_optional_float(y),
        _format_optional_float(get_distance(entry)),
        _format_optional_float(get_angle(entry)),
        get_zone(entry),
        video_display_symbol(get_video(entry)),
    ]


def _visible_columns(app):
    column_vars = getattr(app, "shotlog_column_vars", {})
    selected = [column for column in SHOTLOG_COLUMNS if column_vars.get(column, tk.BooleanVar(value=True)).get()]
    return selected or ["#"]


def _apply_visible_columns(app) -> None:
    if hasattr(app, "shotlog_tree"):
        app.shotlog_tree.configure(displaycolumns=_visible_columns(app))


def _init_column_vars(app) -> None:
    app.shotlog_column_vars = {
        column: tk.BooleanVar(value=column in DEFAULT_VISIBLE_COLUMNS)
        for column in SHOTLOG_COLUMNS
    }


def _close_column_popup(app) -> None:
    popup = getattr(app, "shotlog_column_popup", None)
    if popup is not None:
        try:
            popup.destroy()
        except Exception:
            pass
    app.shotlog_column_popup = None


def _column_popup_position(button) -> tuple[int, int]:
    button.update_idletasks()
    x = button.winfo_rootx()
    y = button.winfo_rooty() + button.winfo_height()
    return x, y


def _create_popup_checkbox(app, parent, column: str, index: int) -> None:
    row = index // COLUMN_POPUP_COLUMNS
    col = index % COLUMN_POPUP_COLUMNS
    checkbox = tb.Checkbutton(
        parent,
        text=_shotlog_heading_text(column),
        variable=app.shotlog_column_vars[column],
        command=lambda: _apply_visible_columns(app),
        bootstyle="primary",
    )
    checkbox.grid(
        row=row,
        column=col,
        sticky="w",
        padx=COLUMN_POPUP_PAD_X,
        pady=COLUMN_POPUP_PAD_Y,
    )


def _open_column_popup(app, button) -> None:
    existing = getattr(app, "shotlog_column_popup", None)
    if existing is not None and existing.winfo_exists():
        _close_column_popup(app)
        return

    popup = tk.Toplevel(button)
    popup.title(COLUMN_POPUP_TITLE)
    popup.transient(app.root)
    popup.resizable(False, False)
    popup.bind("<Escape>", lambda _e: _close_column_popup(app))
    popup.protocol("WM_DELETE_WINDOW", lambda: _close_column_popup(app))
    app.shotlog_column_popup = popup

    frame = tb.Frame(popup, padding=8)
    frame.pack(fill="both", expand=True)

    for index, column in enumerate(SHOTLOG_COLUMNS):
        _create_popup_checkbox(app, frame, column, index)

    close_btn = tb.Button(
        frame,
        text="Close",
        command=lambda: _close_column_popup(app),
        bootstyle="secondary",
    )
    close_btn.grid(row=(len(SHOTLOG_COLUMNS) + COLUMN_POPUP_COLUMNS - 1) // COLUMN_POPUP_COLUMNS, column=0, columnspan=COLUMN_POPUP_COLUMNS, sticky="ew", padx=COLUMN_POPUP_PAD_X, pady=(8, 2))

    x, y = _column_popup_position(button)
    popup.geometry(f"+{x}+{y}")
    popup.lift()


def _create_column_toolbar(app, frame) -> None:
    toolbar = tb.Frame(frame)
    toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PAD_X, pady=(0, PAD_Y))
    _init_column_vars(app)

    button = tb.Button(
        toolbar,
        text=COLUMN_BUTTON_TEXT,
        command=lambda: _open_column_popup(app, button),
        bootstyle="secondary",
    )
    button.pack(anchor="w")


def _configure_shotlog_frame(frame) -> None:
    frame.rowconfigure(1, weight=1)
    frame.columnconfigure(0, weight=1)


def _create_shotlog_tree(frame):
    tree = tb.Treeview(frame, columns=SHOTLOG_COLUMNS, show="headings", bootstyle="primary")
    _configure_shotlog_columns(tree)
    tree.grid(row=1, column=0, sticky="nsew")
    return tree


def _add_scrollbars(frame, tree) -> None:
    v_scrollbar = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
    v_scrollbar.grid(row=1, column=1, sticky="ns")

    h_scrollbar = tb.Scrollbar(frame, orient="horizontal", command=tree.xview)
    h_scrollbar.grid(row=2, column=0, sticky="ew")

    tree.configure(
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set,
    )


def setup_shotlog_frame(app, parent):
    style = tb.Style()
    style.configure(TREEVIEW_STYLE_NAME, font=(SHOTLOG_FONT_FAMILY, SHOTLOG_FONT_SIZE))

    frame = tb.Labelframe(parent, text="Shot Log", bootstyle="primary")
    frame.pack(fill="both", expand=True, padx=PAD_X, pady=PAD_Y)
    _configure_shotlog_frame(frame)
    _create_column_toolbar(app, frame)

    tree = _create_shotlog_tree(frame)
    _add_scrollbars(frame, tree)
    _bind_shotlog_events(tree, app)

    tree._last_hovered_row_id = None
    app.shotlog_tree = tree
    _apply_visible_columns(app)


def update_treeview(tree, entries):
    tree.delete(*tree.get_children())

    for i, entry in enumerate(entries):
        tree.insert("", "end", iid=str(i), values=_entry_values(entry))
