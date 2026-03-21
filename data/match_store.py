import os
import json
import csv
from tkinter import messagebox, filedialog
from gui.plot_controller import update_plot


# === Grundläggande matchhantering ===

def get_match_file(app, name):
    safe_name = name.replace(" ", "_")
    return os.path.join(app.project_root, "Games", f"{safe_name}.json")


def prompt_save_match(app):
    entries = app.get_filtered_entries()
    if not entries:
        messagebox.showinfo("No Data", "There is no match data to save.")
        return

    initial_dir = os.path.join(app.project_root, "Games")
    os.makedirs(initial_dir, exist_ok=True)

    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        initialdir=initial_dir,
        title="Save Match As...",
        initialfile="New Match"
    )
    if not file_path:
        return

    try:
        serializable_entries = [_serialize_entry(e) for e in entries]
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serializable_entries, f, indent=2, ensure_ascii=False)

        name = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")
        # store the *in-memory* entries as tuples (deserialized format)
        app.match_logs[name] = [_deserialize_entry(e) for e in serializable_entries]
        app.current_match.set(name)
        app.update_match_dropdown()
        messagebox.showinfo("Match Saved", f"Match '{name}' was saved.")
    except Exception as e:
        messagebox.showerror("Save Failed", f"Could not save match: {e}")


def load_match_from_file(app):
    file_path = filedialog.askopenfilename(
        title="Select Match File",
        filetypes=[("JSON Match Files", "*.json")],
        initialdir=os.path.join(app.project_root, "Games")
    )
    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        data = [_deserialize_entry(e) for e in raw_data]
        name = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")
        app.match_logs[name] = data
        app.current_match.set(name)
        app.update_match_dropdown()
        load_selected_match(app)
    except Exception as e:
        messagebox.showerror("Load Failed", f"Could not load match: {e}")


def load_selected_match(app):
    name = app.current_match.get()

    if hasattr(app, "delete_match_btn"):
        app.delete_match_btn.config(state="normal" if name not in ["All", "Season"] else "disabled")

    if name in ["All", "Season"]:
        entries = [entry for match in app.match_logs.values() for entry in match]
    else:
        entries = list(app.match_logs.get(name, []))

    app.log_entries = entries
    app.update_shot_log_treeview()
    update_plot(app)
    app.logic.update_stats()
    app.logic.update_expected_goals()


def load_all_matches(app):
    file_paths = filedialog.askopenfilenames(
        title="Load Multiple Matches",
        filetypes=[("JSON Match Files", "*.json")],
        initialdir=os.path.join(app.project_root, "Games")
    )
    if not file_paths:
        return

    combined = {}
    all_entries = []

    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            entries = [_deserialize_entry(e) for e in raw_data]
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
        load_selected_match(app)


def auto_update_current_match(app):
    name = app.current_match.get()
    if name not in ["All", "Season"]:
        file_path = get_match_file(app, name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        entries = app.log_entries
        serializable_entries = [_serialize_entry(e) for e in entries]

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
    load_selected_match(app)


# === CSV-export/import ===

def save_csv_dialog(app):
    name = app.current_match.get() or "All"
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=f"{name}_shots.csv"
    )
    if file_path:
        _save_csv(file_path, app.log_entries)
        messagebox.showinfo("CSV Exported", f"Shots from '{name}' saved.")


def load_csv_dialog(app):
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    name = os.path.splitext(os.path.basename(file_path))[0].replace("_", " ")
    entries = _load_csv(file_path)
    app.match_logs[name] = entries
    with open(get_match_file(app, name), "w", encoding="utf-8") as f:
        json.dump([_serialize_entry(e) for e in entries], f, indent=2, ensure_ascii=False)

    app.update_match_dropdown()
    app.current_match.set(name)
    load_selected_match(app)


def _save_csv(path, entries):
    try:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "#", "S/G", "Phase", "Situation", "Shot Type", "Passer", "Shooter",
                "Period", "xG", "X", "Y", "Pass X", "Pass Y"
            ])
            for e in entries:
                writer.writerow([
                    e[0], e[1], e[2], e[3], e[4], e[5], e[6],
                    e[7], e[8],
                    round(e[9], 2), round(e[10], 2),
                    round(e[11], 2) if e[11] is not None else "",
                    round(e[12], 2) if e[12] is not None else ""
                ])
    except Exception as e:
        print(f"⚠️ CSV Save Error: {e}")


def _load_csv(path):
    entries = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                if len(row) >= 11:
                    entries.append((
                        int(row[0]), row[1], row[2], row[3], row[4],
                        row[5], row[6], row[7], float(row[8]),
                        float(row[9]), float(row[10]),
                        float(row[11]) if len(row) > 11 and row[11] else None,
                        float(row[12]) if len(row) > 12 and row[12] else None,
                        None  # video column not supported in CSV
                    ))
    except Exception as e:
        print(f"⚠️ CSV Load Error: {e}")
    return entries


# === Serializer helpers ===

def _normalize_video(video):
    """
    Ensure we store video as:
      None OR {"path": str, "start": float, "stop": float|None}
    Accepts legacy string too.
    """
    if not video:
        return None
    if isinstance(video, dict):
        path = str(video.get("path") or "")
        if not path:
            return None
        start = float(video.get("start") or 0.0)
        stop = video.get("stop", None)
        stop = None if stop in ("", None) else float(stop)
        return {"path": path, "start": start, "stop": stop}
    # legacy string
    s = str(video).strip()
    if not s:
        return None
    return {"path": s, "start": 0.0, "stop": None}


def _serialize_entry(entry):
    """
    Returns a JSON-safe list length 14.
    Index 13 is a dict or None (never a tuple).
    """
    entry = list(entry) + [None] * (14 - len(entry))
    base = list(entry[:13])
    base.append(_normalize_video(entry[13]))
    return base[:14]


def _deserialize_entry(entry):
    """
    Returns a tuple length 14.
    Upgrades legacy formats so entry[13] becomes dict/None.
    """
    entry = list(entry) + [None] * (14 - len(entry))
    entry[13] = _normalize_video(entry[13])
    return tuple(entry[:14])