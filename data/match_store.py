import json
import os
from tkinter import filedialog, messagebox

from app_paths import MATCHES_DIR
from data.csv_store import load_csv, save_csv
from data.entry_serialization import deserialize_entry, serialize_entry


def get_match_file(app, name):
    safe_name = name.replace(" ", "_")
    return os.path.join(MATCHES_DIR, f"{safe_name}.json")


# ---------------------------------------------------------
# Match save/load/delete
# ---------------------------------------------------------
def prompt_save_match(app):
    entries = app.get_filtered_entries()
    if not entries:
        messagebox.showinfo("No Data", "There is no match data to save.")
        return

    os.makedirs(MATCHES_DIR, exist_ok=True)

    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialdir=MATCHES_DIR,
        title="Save Match As...",
        initialfile="New Match",
    )
    if not file_path:
        return

    try:
        serializable_entries = [serialize_entry(e) for e in entries]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serializable_entries, f, indent=2, ensure_ascii=False)

        name = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")
        app.match_logs[name] = [deserialize_entry(e) for e in serializable_entries]
        app.current_match.set(name)
        app.update_match_dropdown()

        messagebox.showinfo("Match Saved", f"Match '{name}' was saved.")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Could not save match: {e}")


def load_match_from_file(app):
    os.makedirs(MATCHES_DIR, exist_ok=True)

    file_path = filedialog.askopenfilename(
        title="Select Match File",
        filetypes=[("JSON Match Files", "*.json")],
        initialdir=MATCHES_DIR,
    )
    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        data = [deserialize_entry(e) for e in raw_data]
        name = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")

        app.match_logs[name] = data
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
            state="normal" if name not in ["All", "Season"] else "disabled"
        )


def load_all_matches(app, folder=None):
    initial_dir = folder or MATCHES_DIR
    os.makedirs(initial_dir, exist_ok=True)

    file_paths = filedialog.askopenfilenames(
        title="Load Multiple Matches",
        filetypes=[("JSON Match Files", "*.json")],
        initialdir=initial_dir,
    )
    if not file_paths:
        return

    combined = {}
    all_entries = []

    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            entries = [deserialize_entry(e) for e in raw_data]
            name = os.path.splitext(os.path.basename(path))[0].replace("_", " ")

            combined[name] = entries
            all_entries.extend(entries)
        except Exception as e:
            print(f"⚠️ Failed to load {path}: {e}")

    if combined:
        app.match_logs.update(combined)

    if all_entries:
        app.match_logs["Season"] = all_entries
        app.current_match.set("Season")


def auto_update_current_match(app):
    name = app.current_match.get()
    if name not in ["All", "Season"]:
        file_path = get_match_file(app, name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        entries = app.log_entries
        serializable_entries = [serialize_entry(e) for e in entries]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serializable_entries, f, indent=2, ensure_ascii=False)


def delete_current_match(app):
    name = app.current_match.get()
    if name in ["All", "Season"] or name not in app.match_logs:
        return

    if not messagebox.askyesno("Delete Match", f"Delete match '{name}'?"):
        return

    del app.match_logs[name]

    file_path = get_match_file(app, name)
    if os.path.exists(file_path):
        os.remove(file_path)

    app.current_match.set(next(iter(app.match_logs)) if app.match_logs else "New Match")
    app.update_match_dropdown()


# ---------------------------------------------------------
# CSV import/export
# ---------------------------------------------------------
def save_csv_dialog(app):
    name = app.current_match.get() or "All"

    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=f"{name}_shots.csv",
    )

    if file_path:
        try:
            save_csv(file_path, app.log_entries)
            messagebox.showinfo("CSV Exported", f"Shots from '{name}' saved.")
        except Exception as e:
            messagebox.showerror("CSV Export Failed", f"Could not save CSV: {e}")


def load_csv_dialog(app):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    try:
        entries = load_csv(file_path)
        app.match_logs["New Match"] = entries
        app.current_match.set("New Match")
        app.update_match_dropdown()
        messagebox.showinfo("CSV Loaded", "CSV data loaded into New Match.")
    except Exception as e:
        messagebox.showerror("CSV Import Failed", f"Could not load CSV: {e}")