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
# The shot log has horizontal scrolling, so all available fields can be shown by default.
DEFAULT_VISIBLE_COLUMNS = SHOTLOG_COLUMNS
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
COLUMN_POPUP_COLUMNS = 3
COLUMN_POPUP_PAD_X = 12
COLUMN_POPUP_PAD_Y = 5
COLUMN_POPUP_PADDING = 10
MATCH_BUTTON_ALL_TEXT = "Matches: All ▾"
MATCH_BUTTON_PREFIX = "Matches"
MATCH_POPUP_TITLE = "Shot Log Matches"
MATCH_POPUP_PADDING = 10
MATCH_SPECIAL_NAMES = ("All", "Season")
MATCH_ALL_LABEL = "All matches"


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
    y = button.winfo_rooty() + button.winfo_height() + 4
    return x, y


def _create_popup_checkbox(app, parent, column: str, index: int) -> None:
    row = index // COLUMN_POPUP_COLUMNS
    col = index % COLUMN_POPUP_COLUMNS
    checkbox = tb.Checkbutton(
        parent,
        text=_shotlog_heading_text(column),
        variable=app.shotlog_column_vars[column],
        command=lambda: _apply_visible_columns(app),
        bootstyle="round-toggle",
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

    frame = tb.Frame(popup, padding=COLUMN_POPUP_PADDING)
    frame.pack(fill="both", expand=True)

    for index, column in enumerate(SHOTLOG_COLUMNS):
        _create_popup_checkbox(app, frame, column, index)

    close_btn = tb.Button(
        frame,
        text="Done",
        command=lambda: _close_column_popup(app),
        bootstyle="secondary",
    )
    close_btn.grid(
        row=(len(SHOTLOG_COLUMNS) + COLUMN_POPUP_COLUMNS - 1) // COLUMN_POPUP_COLUMNS,
        column=0,
        columnspan=COLUMN_POPUP_COLUMNS,
        sticky="ew",
        padx=COLUMN_POPUP_PAD_X,
        pady=(10, 2),
    )

    x, y = _column_popup_position(button)
    popup.geometry(f"+{x}+{y}")
    popup.lift()


def _match_names(app):
    return [name for name in app.match_logs.keys() if name not in MATCH_SPECIAL_NAMES]


def _init_match_filter_vars(app) -> None:
    if not hasattr(app, "shotlog_match_filter_all"):
        app.shotlog_match_filter_all = tk.BooleanVar(value=True)
    if not hasattr(app, "shotlog_match_filter_vars"):
        app.shotlog_match_filter_vars = {}

    current_names = set(_match_names(app))
    for name in current_names:
        app.shotlog_match_filter_vars.setdefault(name, tk.BooleanVar(value=False))

    for name in list(app.shotlog_match_filter_vars.keys()):
        if name not in current_names:
            del app.shotlog_match_filter_vars[name]

    if not any(var.get() for var in app.shotlog_match_filter_vars.values()):
        app.shotlog_match_filter_all.set(True)


def _selected_match_count(app) -> int:
    return sum(1 for var in getattr(app, "shotlog_match_filter_vars", {}).values() if var.get())


def _update_match_filter_button_text(app) -> None:
    button = getattr(app, "shotlog_match_filter_button", None)
    if button is None:
        return

    if getattr(app, "shotlog_match_filter_all", tk.BooleanVar(value=True)).get():
        button.configure(text=MATCH_BUTTON_ALL_TEXT)
        return

    selected = [name for name, var in app.shotlog_match_filter_vars.items() if var.get()]
    if len(selected) == 1:
        button.configure(text=f"{MATCH_BUTTON_PREFIX}: {selected[0]} ▾")
    else:
        button.configure(text=f"{MATCH_BUTTON_PREFIX}: {len(selected)} ▾")


def sync_match_filter_controls(app) -> None:
    _init_match_filter_vars(app)
    _update_match_filter_button_text(app)


def _apply_match_filter(app) -> None:
    _update_match_filter_button_text(app)
    app.refresh_all()


def _on_all_matches_toggled(app) -> None:
    if app.shotlog_match_filter_all.get():
        for var in app.shotlog_match_filter_vars.values():
            var.set(False)
    elif _selected_match_count(app) == 0:
        app.shotlog_match_filter_all.set(True)
    _apply_match_filter(app)


def _on_match_toggled(app) -> None:
    if _selected_match_count(app) > 0:
        app.shotlog_match_filter_all.set(False)
    else:
        app.shotlog_match_filter_all.set(True)
    _apply_match_filter(app)


def _close_match_popup(app) -> None:
    popup = getattr(app, "shotlog_match_popup", None)
    if popup is not None:
        try:
            popup.destroy()
        except Exception:
            pass
    app.shotlog_match_popup = None


def _open_match_popup(app, button) -> None:
    existing = getattr(app, "shotlog_match_popup", None)
    if existing is not None and existing.winfo_exists():
        _close_match_popup(app)
        return

    _init_match_filter_vars(app)

    popup = tk.Toplevel(button)
    popup.title(MATCH_POPUP_TITLE)
    popup.transient(app.root)
    popup.resizable(False, False)
    popup.bind("<Escape>", lambda _e: _close_match_popup(app))
    popup.protocol("WM_DELETE_WINDOW", lambda: _close_match_popup(app))
    app.shotlog_match_popup = popup

    frame = tb.Frame(popup, padding=MATCH_POPUP_PADDING)
    frame.pack(fill="both", expand=True)

    all_checkbox = tb.Checkbutton(
        frame,
        text=MATCH_ALL_LABEL,
        variable=app.shotlog_match_filter_all,
        command=lambda: _on_all_matches_toggled(app),
        bootstyle="round-toggle",
    )
    all_checkbox.pack(anchor="w", padx=8, pady=(4, 8))

    tb.Separator(frame, orient="horizontal").pack(fill="x", pady=(0, 8))

    for name in _match_names(app):
        checkbox = tb.Checkbutton(
            frame,
            text=name,
            variable=app.shotlog_match_filter_vars[name],
            command=lambda: _on_match_toggled(app),
            bootstyle="round-toggle",
        )
        checkbox.pack(anchor="w", padx=8, pady=3)

    close_btn = tb.Button(
        frame,
        text="Done",
        command=lambda: _close_match_popup(app),
        bootstyle="secondary",
    )
    close_btn.pack(fill="x", padx=8, pady=(10, 2))

    x, y = _column_popup_position(button)
    popup.geometry(f"+{x}+{y}")
    popup.lift()


def _create_column_toolbar(app, frame) -> None:
    toolbar = tb.Frame(frame)
    toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PAD_X, pady=(0, PAD_Y))
    _init_column_vars(app)
    _init_match_filter_vars(app)

    column_button = tb.Button(
        toolbar,
        text=COLUMN_BUTTON_TEXT,
        command=lambda: _open_column_popup(app, column_button),
        bootstyle="secondary",
    )
    column_button.pack(side="left")

    match_button = tb.Button(
        toolbar,
        text=MATCH_BUTTON_ALL_TEXT,
        command=lambda: _open_match_popup(app, match_button),
        bootstyle="secondary",
    )
    match_button.pack(side="left", padx=(6, 0))
    app.shotlog_match_filter_button = match_button
    _update_match_filter_button_text(app)


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

    frame = tb.Labelframe(parent, text="Shot Log", bootstyle="secondary")
    frame.pack(fill="both", expand=True, padx=PAD_X, pady=PAD_Y)
    _configure_shotlog_frame(frame)
    _create_column_toolbar(app, frame)
    app.sync_shotlog_match_filter = lambda: sync_match_filter_controls(app)

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
