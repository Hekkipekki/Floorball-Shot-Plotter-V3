import json
import os
from tkinter import filedialog, messagebox

from app_paths import MATCHES_DIR
from data.csv_store import load_csv, save_csv
from data.entry_serialization import deserialize_entry, serialize_entry

READ_ONLY_MATCHES = ("All", "Season")
DEFAULT_MATCH_NAME = "New Match"
SEASON_MATCH_NAME = "Season"
JSON_FILETYPES = [("JSON Match Files", "*.json")]
CSV_FILETYPES = [("CSV files", "*.csv")]


def _match_name_from_path(file_path):
    return os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")


def _safe_match_filename(name):
    return name.replace(" ", "_")


def _ensure_matches_dir(path=MATCHES_DIR):
    os.makedirs(path, exist_ok=True)


def _serialize_entries(entries):
    return [serialize_entry(e) for e in entries]


def _deserialize_entries(entries):
    return [deserialize_entry(e) for e in entries]


def _write_json_entries(file_path, entries):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(_serialize_entries(entries), f, indent=2, ensure_ascii=False)


def _read_json_entries(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    return _deserialize_entries(raw_data)


def _is_editable_match(name):
    return name not in READ_ONLY_MATCHES


def get_match_file(app, name):
    return os.path.join(MATCHES_DIR, f"{_safe_match_filename(name)}.json")


# ---------------------------------------------------------
# Match save/load/delete
# ---------------------------------------------------------
def prompt_save_match(app):
    entries = app.get_filtered_entries()
    if not entries:
        messagebox.showinfo("No Data", "There is no match data to save.")
        return

    _ensure_matches_dir()

    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=JSON_FILETYPES,
        initialdir=MATCHES_DIR,
        title="Save Match As...",
        initialfile=DEFAULT_MATCH_NAME,
    )
    if not file_path:
        return

    try:
        _write_json_entries(file_path, entries)

        name = _match_name_from_path(file_path)
        app.match_logs[name] = list(entries)
        app.current_match.set(name)
        app.update_match_dropdown()

        messagebox.showinfo("Match Saved", f"Match '{name}' was saved.")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Could not save match: {e}")


def load_match_from_file(app):
    _ensure_matches_dir()

    file_path = filedialog.askopenfilename(
        title="Select Match File",
        filetypes=JSON_FILETYPES,
        initialdir=MATCHES_DIR,
    )
    if not file_path:
        return

    try:
        name = _match_name_from_path(file_path)
        app.match_logs[name] = _read_json_entries(file_path)
        app.current_match.set(name)
        app.update_match_dropdown()
    except Exception as e:
        messagebox.showerror("Load Failed", f"Could not load match: {e}")


def load_selected_match(app):
    """
    Select the current match only.
    UI refresh is handled by the controller.
    """
    name = app.current_match.get()

    if hasattr(app, "delete_match_btn"):
        app.delete_match_btn.config(
            state="normal" if _is_editable_match(name) else "disabled"
        )


def load_all_matches(app, folder=None):
    initial_dir = folder or MATCHES_DIR
    _ensure_matches_dir(initial_dir)

    file_paths = filedialog.askopenfilenames(
        title="Load Multiple Matches",
        filetypes=JSON_FILETYPES,
        initialdir=initial_dir,
    )
    if not file_paths:
        return

    combined = {}
    all_entries = []

    for path in file_paths:
        try:
            entries = _read_json_entries(path)
            name = _match_name_from_path(path)

            combined[name] = entries
            all_entries.extend(entries)
        except Exception as e:
            print(f"⚠️ Failed to load {path}: {e}")

    if combined:
        app.match_logs.update(combined)

    if all_entries:
        app.match_logs[SEASON_MATCH_NAME] = all_entries
        app.current_match.set(SEASON_MATCH_NAME)


def auto_update_current_match(app):
    name = app.current_match.get()
    if not _is_editable_match(name):
        return

    file_path = get_match_file(app, name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    _write_json_entries(file_path, app.log_entries)


def delete_current_match(app):
    name = app.current_match.get()
    if not _is_editable_match(name) or name not in app.match_logs:
        return

    if not messagebox.askyesno("Delete Match", f"Delete match '{name}'?"):
        return

    del app.match_logs[name]

    file_path = get_match_file(app, name)
    if os.path.exists(file_path):
        os.remove(file_path)

    app.current_match.set(
        next(iter(app.match_logs)) if app.match_logs else DEFAULT_MATCH_NAME
    )
    app.update_match_dropdown()


# ---------------------------------------------------------
# CSV import/export
# ---------------------------------------------------------
def save_csv_dialog(app):
    name = app.current_match.get() or "All"

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=CSV_FILETYPES,
        initialfile=f"{name}_shots.csv",
    )

    if file_path:
        try:
            save_csv(file_path, app.log_entries)
            messagebox.showinfo("CSV Exported", f"Shots from '{name}' saved.")
        except Exception as e:
            messagebox.showerror("CSV Export Failed", f"Could not save CSV: {e}")


def load_csv_dialog(app):
    file_path = filedialog.askopenfilename(filetypes=CSV_FILETYPES)
    if not file_path:
        return

    try:
        entries = load_csv(file_path)
        app.match_logs[DEFAULT_MATCH_NAME] = entries
        app.current_match.set(DEFAULT_MATCH_NAME)
        app.update_match_dropdown()
        messagebox.showinfo("CSV Loaded", "CSV data loaded into New Match.")
    except Exception as e:
        messagebox.showerror("CSV Import Failed", f"Could not load CSV: {e}")
