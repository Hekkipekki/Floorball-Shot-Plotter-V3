import ttkbootstrap as tb
from PIL import Image, ImageTk

from assets import get_icon_path
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
    SHOTLOG_VIDEO_ICON_BG,
    SHOTLOG_VIDEO_ICON_SIZE,
)
from gui.shotlog_video import video_display_symbol, open_video_menu
from gui.shotlog_interactions import (
    on_hover_shot,
    on_leave_shotlog,
    on_row_double_click,
)

SHOTLOG_COLUMNS = ("#", "S/G", "Phase", "Situation", "Type", "Passer", "Shooter", "P", "xG", "Video")
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
    "Video": SHOTLOG_COL_WIDTH_VIDEO,
}


def _shotlog_heading_text(column: str) -> str:
    return "🎬" if column == "Video" else column


def _configure_shotlog_columns(tree: tb.Treeview) -> None:
    for column in SHOTLOG_COLUMNS:
        tree.heading(column, text=_shotlog_heading_text(column))
        tree.column(column, anchor="center", width=SHOTLOG_COLUMN_WIDTHS.get(column, 60), stretch=False)


def _bind_shotlog_events(tree: tb.Treeview, app) -> None:
    tree.bind("<Motion>", lambda e: on_hover_shot(e, tree, app))
    tree.bind("<Leave>", lambda e: on_leave_shotlog(e, tree, app))
    tree.bind("<Double-1>", lambda e: on_row_double_click(e, tree, app))
    tree.bind("<Button-3>", lambda e: open_video_menu(e, tree, app))


def _entry_values(entry) -> list:
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
        video_display_symbol(get_video(entry)),
    ]


def setup_shotlog_frame(app, parent):
    style = tb.Style()
    style.configure("Treeview", font=(SHOTLOG_FONT_FAMILY, SHOTLOG_FONT_SIZE))

    frame = tb.Labelframe(parent, text="Shot Log", bootstyle="primary")
    frame.pack(fill="both", expand=True, padx=PAD_X, pady=PAD_Y)
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)

    tree = tb.Treeview(frame, columns=SHOTLOG_COLUMNS, show="headings", bootstyle="primary")
    _configure_shotlog_columns(tree)

    tree.grid(row=0, column=0, sticky="nsew")

    v_scrollbar = tb.Scrollbar(frame, orient="vertical", command=tree.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns")

    h_scrollbar = tb.Scrollbar(frame, orient="horizontal", command=tree.xview)
    h_scrollbar.grid(row=1, column=0, sticky="ew")

    tree.configure(
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set,
    )

    _bind_shotlog_events(tree, app)

    tree._last_hovered_row_id = None
    app.shotlog_tree = tree


def update_treeview(tree, entries):
    tree.delete(*tree.get_children())

    for i, entry in enumerate(entries):
        tree.insert("", "end", iid=str(i), values=_entry_values(entry))
