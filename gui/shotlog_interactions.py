from tkinter import messagebox

from core.entry_helpers import get_number

READ_ONLY_MATCHES = ("All", "Season")
RESET_CONFIRM_TITLE = "Confirm Reset"
RESET_CONFIRM_MESSAGE = "Are you sure you want to reset all data?"


def _current_match(app):
    return app.current_match.get()


def _is_editable_match(match_name: str) -> bool:
    return match_name not in READ_ONLY_MATCHES


def _safe_auto_save_current_match(app) -> None:
    try:
        app.auto_update_current_match()
    except Exception as e:
        print("⚠️ Auto-save current match failed:", e)


def _safe_row_index(iid):
    try:
        return int(iid)
    except (TypeError, ValueError):
        return None


def reset_shot_log(app):
    if not messagebox.askyesno(RESET_CONFIRM_TITLE, RESET_CONFIRM_MESSAGE):
        return
    app.log_entries.clear()
    app.update_shot_log_treeview()
    app.update_plot()
    app.update_stats()


def find_master_entry_index(app, entry):
    current_match = _current_match(app)
    if not _is_editable_match(current_match):
        return None

    match_entries = app.match_logs.get(current_match, [])
    entry_number = get_number(entry)

    for i, candidate in enumerate(match_entries):
        if get_number(candidate) == entry_number:
            return i

    return None


def update_entry_in_all_places(app, visible_index, updated_entry):
    if not (0 <= visible_index < len(app.log_entries)):
        return

    app.log_entries[visible_index] = tuple(updated_entry)

    master_index = find_master_entry_index(app, app.log_entries[visible_index])
    current_match = _current_match(app)

    if master_index is not None and current_match in app.match_logs:
        match_entries = list(app.match_logs[current_match])
        match_entries[master_index] = tuple(updated_entry)
        app.match_logs[current_match] = match_entries

    app.update_shot_log_treeview()
    _safe_auto_save_current_match(app)


def _delete_from_current_match(app, current_match, current_entry) -> bool:
    if not _is_editable_match(current_match):
        return False

    master_index = find_master_entry_index(app, current_entry)
    if master_index is None:
        return False

    del app.match_logs[current_match][master_index]
    app.update_log_view_and_stats()
    app.auto_update_current_match()
    return True


def _delete_from_visible_log(app, index) -> None:
    del app.log_entries[index]
    app.update_shot_log_treeview()
    app.update_plot()
    app.update_stats()


def on_row_double_click(event, tree, app):
    iid = tree.identify_row(event.y)
    index = _safe_row_index(iid)
    if index is None or not (0 <= index < len(app.log_entries)):
        return

    try:
        current_entry = app.log_entries[index]
        current_match = _current_match(app)

        if _delete_from_current_match(app, current_match, current_entry):
            return

        _delete_from_visible_log(app, index)
    except Exception as e:
        print("Double-click error:", e)


def _clear_hover(app, tree) -> None:
    tree._last_hovered_row_id = None
    app.clear_highlight()


def on_hover_shot(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        if tree._last_hovered_row_id is not None:
            _clear_hover(app, tree)
        return

    if iid == tree._last_hovered_row_id:
        return

    try:
        index = int(iid)
        if 0 <= index < len(app.log_entries):
            tree._last_hovered_row_id = iid
            app.highlight_point(index)
    except Exception as e:
        print("Hover error:", e)
        _clear_hover(app, tree)


def on_leave_shotlog(event, tree, app):
    if tree._last_hovered_row_id is not None:
        _clear_hover(app, tree)
