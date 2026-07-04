import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import webbrowser

from core.schema import IDX_VIDEO, ENTRY_LENGTH

DEFAULT_VIDEO_START = 0.0
VIDEO_FILETYPES = [("Video Files", "*.mp4 *.mov *.avi *.mkv")]
VIDEO_SYMBOL = "🎬"


def video_to_dict(video):
    if not video:
        return None
    if isinstance(video, dict):
        return video
    return {"path": str(video), "start": DEFAULT_VIDEO_START, "stop": None}


def video_display_symbol(video):
    v = video_to_dict(video)
    return VIDEO_SYMBOL if v and v.get("path") else ""


def ensure_video_field(app, index):
    entry = list(app.log_entries[index])
    if len(entry) < ENTRY_LENGTH:
        entry += [None] * (ENTRY_LENGTH - len(entry))
        app._shotlog_update_entry(index, entry)


def _entry_with_video_field(app, index):
    ensure_video_field(app, index)
    return list(app.log_entries[index])


def set_video_dict(app, index, path_or_url: str):
    entry = _entry_with_video_field(app, index)
    entry[IDX_VIDEO] = {"path": path_or_url, "start": DEFAULT_VIDEO_START, "stop": None}
    app._shotlog_update_entry(index, entry)


def link_offline(app, index):
    path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=VIDEO_FILETYPES,
    )
    if path:
        set_video_dict(app, index, path)


def link_online(app, index):
    url = simpledialog.askstring("Link Online Video", "Enter video URL:")
    if url:
        set_video_dict(app, index, url)


def remove_video(app, index):
    entry = _entry_with_video_field(app, index)
    entry[IDX_VIDEO] = None
    app._shotlog_update_entry(index, entry)


def _save_video_segment(app, index, path, new_start, new_stop) -> None:
    entry = _entry_with_video_field(app, index)
    video = video_to_dict(entry[IDX_VIDEO]) or {
        "path": path,
        "start": DEFAULT_VIDEO_START,
        "stop": None,
    }
    video["start"] = float(new_start or DEFAULT_VIDEO_START)
    video["stop"] = None if new_stop in ("", None) else float(new_stop)
    entry[IDX_VIDEO] = video
    app._shotlog_update_entry(index, entry)


def _play_local_video(app, path, start, stop, on_save_segment) -> None:
    if not os.path.exists(path):
        messagebox.showwarning("Video Missing", "Video file could not be found.")
        return

    from utils.videoplayer import show_video_overlay

    show_video_overlay(
        app,
        path,
        start=start,
        stop=stop,
        autoplay=True,
        on_save_segment=on_save_segment,
    )


def play_or_edit_video(app, index):
    ensure_video_field(app, index)
    video = video_to_dict(app.log_entries[index][IDX_VIDEO])
    if not video or not video.get("path"):
        return

    path = video["path"]
    start = float(video.get("start") or DEFAULT_VIDEO_START)
    stop = video.get("stop", None)

    def save_segment_cb(new_start, new_stop):
        _save_video_segment(app, index, path, new_start, new_stop)

    try:
        if str(path).startswith("http"):
            webbrowser.open(path)
        else:
            _play_local_video(app, path, start, stop, save_segment_cb)
    except Exception as e:
        messagebox.showerror("Playback Failed", f"Could not play video:\n{e}")


def _selected_row_index(event, tree, app):
    iid = tree.identify_row(event.y)
    if not iid:
        return None

    tree.selection_set(iid)
    index = int(iid)
    if not (0 <= index < len(app.log_entries)):
        return None

    return index


def _add_existing_video_menu_items(menu, app, index) -> None:
    menu.add_command(
        label="🎬 Play / Edit Segment",
        command=lambda: play_or_edit_video(app, index),
    )
    menu.add_separator()
    menu.add_command(
        label="🎞️ Relink Offline Video",
        command=lambda: link_offline(app, index),
    )
    menu.add_command(
        label="🌐 Relink Online Video",
        command=lambda: link_online(app, index),
    )
    menu.add_separator()
    menu.add_command(
        label="❌ Remove Video Link",
        command=lambda: remove_video(app, index),
    )


def _add_new_video_menu_items(menu, app, index) -> None:
    menu.add_command(
        label="🎞️ Link Offline Video",
        command=lambda: link_offline(app, index),
    )
    menu.add_command(
        label="🌐 Link Online Video",
        command=lambda: link_online(app, index),
    )


def open_video_menu(event, tree, app):
    index = _selected_row_index(event, tree, app)
    if index is None:
        return

    ensure_video_field(app, index)
    current_video = video_to_dict(app.log_entries[index][IDX_VIDEO])
    has_video = bool(current_video and current_video.get("path"))

    menu = tk.Menu(tree, tearoff=0)

    if has_video:
        _add_existing_video_menu_items(menu, app, index)
    else:
        _add_new_video_menu_items(menu, app, index)

    menu.post(event.x_root, event.y_root)
