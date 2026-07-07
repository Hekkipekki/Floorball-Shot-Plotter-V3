import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from core.schema import IDX_VIDEO, ENTRY_LENGTH
from paths import VIDEOS_DIR, ensure_data_dirs
from utils.render_progress import close_render_progress, show_render_progress
from utils.video_clip_exporter import VideoClipExportError, export_local_segment
from utils.youtube_resolver import OnlineVideoError, is_http_url, resolve_online_video

DEFAULT_VIDEO_START = 0.0
VIDEO_FILETYPES = [("Video Files", "*.mp4 *.mov *.avi *.mkv")]
VIDEO_SYMBOL = "🎬"
CLIP_FILETYPES = [("MP4 Video", "*.mp4")]


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


def set_video_dict(app, index, path_or_url: str, start: float = DEFAULT_VIDEO_START, stop=None):
    entry = _entry_with_video_field(app, index)
    entry[IDX_VIDEO] = {"path": path_or_url, "start": float(start or DEFAULT_VIDEO_START), "stop": stop}
    app._shotlog_update_entry(index, entry)


def link_offline(app, index):
    path = filedialog.askopenfilename(
        title="Select Video File",
        filetypes=VIDEO_FILETYPES,
    )
    if path:
        set_video_dict(app, index, path)


def link_online(app, index):
    url = simpledialog.askstring("Link Online Video", "Enter YouTube / video URL:")
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
    video["path"] = path
    video["start"] = float(new_start or DEFAULT_VIDEO_START)
    video["stop"] = None if new_stop in ("", None) else float(new_stop)
    entry[IDX_VIDEO] = video
    app._shotlog_update_entry(index, entry)


def _default_clip_name(source_path: str, start: float, stop: float | None) -> str:
    source_stem = Path(source_path).stem or "shot_clip"
    start_label = int(max(0.0, float(start or 0.0)))
    stop_label = "end" if stop is None else int(max(0.0, float(stop)))
    return f"{source_stem}_{start_label}s-{stop_label}s.mp4"


def _ask_clip_output_path(source_path: str, start: float, stop: float | None) -> str | None:
    ensure_data_dirs()
    return filedialog.asksaveasfilename(
        title="Export Short Clip",
        initialdir=str(VIDEOS_DIR),
        initialfile=_default_clip_name(source_path, start, stop),
        defaultextension=".mp4",
        filetypes=CLIP_FILETYPES,
    )


def _export_local_clip_and_link(app, index, path, start, stop) -> None:
    if is_http_url(path):
        raise VideoClipExportError("Export Clip is only available for local video files.")

    output_path = _ask_clip_output_path(path, start, stop)
    if not output_path:
        return

    progress = show_render_progress(app, message="Exporting and compressing selected video segment...\nPlease wait.")
    try:
        exported = export_local_segment(path, output_path, start=start, stop=stop)
    finally:
        close_render_progress(progress)

    clip_duration = None if stop is None else max(0.0, float(stop) - float(start or 0.0))
    set_video_dict(app, index, str(exported), start=0.0, stop=clip_duration)
    messagebox.showinfo("Clip Exported", "The shorter clip was exported and linked to this Shot Log row.")


def _play_local_video(app, path, start, stop, on_save_segment, on_export_segment=None) -> None:
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
        on_export_segment=on_export_segment,
        video_source_id=path,
    )


def _play_online_video(app, url, start, stop, on_save_segment) -> None:
    from utils.videoplayer import show_video_overlay

    try:
        resolved = resolve_online_video(url)
    except OnlineVideoError as exc:
        messagebox.showerror("Online Video Failed", str(exc))
        return

    show_video_overlay(
        app,
        resolved.playback_url,
        start=start,
        stop=stop,
        autoplay=True,
        on_save_segment=on_save_segment,
        on_export_segment=None,
        video_source_id=url,
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

    def export_segment_cb(new_start, new_stop):
        _export_local_clip_and_link(app, index, path, new_start, new_stop)

    try:
        if is_http_url(str(path)):
            _play_online_video(app, path, start, stop, save_segment_cb)
        else:
            _play_local_video(app, path, start, stop, save_segment_cb, export_segment_cb)
    except Exception as e:
        messagebox.showerror("Playback Failed", f"Could not play video:\n{e}")


def export_video_segment(app, index):
    ensure_video_field(app, index)
    video = video_to_dict(app.log_entries[index][IDX_VIDEO])
    if not video or not video.get("path"):
        return
    path = video["path"]
    if is_http_url(str(path)):
        messagebox.showinfo("Export Clip", "Export Clip is only available for local video files.")
        return
    start = float(video.get("start") or DEFAULT_VIDEO_START)
    stop = video.get("stop", None)
    try:
        _export_local_clip_and_link(app, index, path, start, stop)
    except Exception as e:
        messagebox.showerror("Export Clip Failed", str(e))


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
    current_video = video_to_dict(app.log_entries[index][IDX_VIDEO])
    path = str(current_video.get("path", "")) if current_video else ""
    is_online = is_http_url(path)

    menu.add_command(
        label="🎬 Play / Edit Segment",
        command=lambda: play_or_edit_video(app, index),
    )
    if not is_online:
        menu.add_command(
            label="✂ Export Segment to Clip",
            command=lambda: export_video_segment(app, index),
        )
    menu.add_separator()
    menu.add_command(
        label="🎞️ Relink Offline Video",
        command=lambda: link_offline(app, index),
    )
    menu.add_command(
        label="🌐 Relink Online / YouTube Video",
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
        label="🌐 Link Online / YouTube Video",
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
