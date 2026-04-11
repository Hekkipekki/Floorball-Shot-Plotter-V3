from tkinter import messagebox
from core.schema import IDX_NUMBER


def reset_shot_log(app):
    if not messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data?"):
        return
    app.log_entries.clear()
    app.update_shot_log_treeview()
    app.update_plot()
    app.update_stats()


def find_master_entry_index(app, entry):
    current_match = app.current_match.get()
    if current_match in ("All", "Season"):
        return None

    match_entries = app.match_logs.get(current_match, [])
    entry_number = entry[IDX_NUMBER]

    for i, candidate in enumerate(match_entries):
        if len(candidate) > 0 and candidate[IDX_NUMBER] == entry_number:
            return i

    return None


def update_entry_in_all_places(app, visible_index, updated_entry):
    if not (0 <= visible_index < len(app.log_entries)):
        return

    app.log_entries[visible_index] = tuple(updated_entry)

    master_index = find_master_entry_index(app, app.log_entries[visible_index])
    current_match = app.current_match.get()

    if master_index is not None and current_match in app.match_logs:
        match_entries = list(app.match_logs[current_match])
        match_entries[master_index] = tuple(updated_entry)
        app.match_logs[current_match] = match_entries

    app.update_shot_log_treeview()

    try:
        app.auto_update_current_match()
    except Exception as e:
        print("⚠️ Auto-save current match failed:", e)


def on_row_double_click(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        return
    try:
        index = int(iid)
        if 0 <= index < len(app.log_entries):
            current_entry = app.log_entries[index]
            current_match = app.current_match.get()

            if current_match not in ("All", "Season"):
                master_index = find_master_entry_index(app, current_entry)
                if master_index is not None:
                    del app.match_logs[current_match][master_index]
                    app.update_log_view_and_stats()
                    app.auto_update_current_match()
                    return

            del app.log_entries[index]
            app.update_shot_log_treeview()
            app.update_plot()
            app.update_stats()
    except Exception as e:
        print("Double-click error:", e)


def on_hover_shot(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        if tree._last_hovered_row_id is not None:
            tree._last_hovered_row_id = None
            app.clear_highlight()
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
        app.clear_highlight()
        tree._last_hovered_row_id = None


def on_leave_shotlog(event, tree, app):
    if tree._last_hovered_row_id is not None:
        tree._last_hovered_row_id = None
        app.clear_highlight()