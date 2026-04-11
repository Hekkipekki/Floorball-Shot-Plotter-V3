import os
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import webbrowser

from core.schema import IDX_VIDEO, ENTRY_LENGTH


def video_to_dict(video):
    if not video:
        return None
    if isinstance(video, dict):
        return video
    return {"path": str(video), "start": 0.0, "stop": None}


def video_display_symbol(video):
    v = video_to_dict(video)
    return "🎬" if v and v.get("path") else ""


def ensure_video_field(app, index):
    entry = list(app.log_entries[index])
    if len(entry) < ENTRY_LENGTH:
        entry += [None] * (ENTRY_LENGTH - len(entry))
        app._shotlog_update_entry(index, entry)


def set_video_dict(app, index, path_or_url: str):
    ensure_video_field(app, index)
    entry = list(app.log_entries[index])
    entry[IDX_VIDEO] = {"path": path_or_url, "start": 0.0, "stop": None}
    app._shotlog_update_entry(index, entry)


def link_offline(app, index):
    path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")]
    )
    if path:
        set_video_dict(app, index, path)


def link_online(app, index):
    url = simpledialog.askstring("Link Online Video", "Enter video URL:")
    if url:
        set_video_dict(app, index, url)


def remove_video(app, index):
    ensure_video_field(app, index)
    entry = list(app.log_entries[index])
    entry[IDX_VIDEO] = None
    app._shotlog_update_entry(index, entry)


def play_or_edit_video(app, index):
    ensure_video_field(app, index)
    video = video_to_dict(app.log_entries[index][IDX_VIDEO])
    if not video or not video.get("path"):
        return

    path = video["path"]
    start = float(video.get("start") or 0.0)
    stop = video.get("stop", None)

    def save_segment_cb(new_start, new_stop):
        ensure_video_field(app, index)
        entry = list(app.log_entries[index])
        v = video_to_dict(entry[IDX_VIDEO]) or {"path": path, "start": 0.0, "stop": None}
        v["start"] = float(new_start or 0.0)
        v["stop"] = None if new_stop in ("", None) else float(new_stop)
        entry[IDX_VIDEO] = v
        app._shotlog_update_entry(index, entry)

    try:
        if str(path).startswith("http"):
            webbrowser.open(path)
        else:
            if os.path.exists(path):
                from utils.videoplayer import show_video_overlay

                show_video_overlay(
                    app,
                    path,
                    start=start,
                    stop=stop,
                    autoplay=True,
                    on_save_segment=save_segment_cb,
                )
            else:
                messagebox.showwarning("Video Missing", "Video file could not be found.")
    except Exception as e:
        messagebox.showerror("Playback Failed", f"Could not play video:\n{e}")


def open_video_menu(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        return

    tree.selection_set(iid)
    index = int(iid)

    if not (0 <= index < len(app.log_entries)):
        return

    ensure_video_field(app, index)
    current_video = video_to_dict(app.log_entries[index][IDX_VIDEO])
    has_video = bool(current_video and current_video.get("path"))

    menu = tk.Menu(tree, tearoff=0)

    if has_video:
        menu.add_command(label="🎬 Play / Edit Segment", command=lambda: play_or_edit_video(app, index))
        menu.add_separator()
        menu.add_command(label="🎞️ Relink Offline Video", command=lambda: link_offline(app, index))
        menu.add_command(label="🌐 Relink Online Video", command=lambda: link_online(app, index))
        menu.add_separator()
        menu.add_command(label="❌ Remove Video Link", command=lambda: remove_video(app, index))
    else:
        menu.add_command(label="🎞️ Link Offline Video", command=lambda: link_offline(app, index))
        menu.add_command(label="🌐 Link Online Video", command=lambda: link_online(app, index))

    menu.post(event.x_root, event.y_root)