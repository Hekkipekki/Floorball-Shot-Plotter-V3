"""Link video-player segments to shots/goals created from video plotting."""

from __future__ import annotations

import os
from pathlib import Path
from tkinter import messagebox

from core.schema import IDX_VIDEO
from paths import VIDEOS_DIR, ensure_data_dirs
from utils.render_progress import close_render_progress, show_render_progress, update_render_progress
from utils.video_clip_exporter import VideoClipExportError, export_local_segment_async
from utils.youtube_resolver import is_http_url

PENDING_VIDEO_ATTR = "pending_video_segment_for_next_event"
DEFAULT_VIDEO_START = 0.0


def _safe_stem(value: str) -> str:
    stem = Path(value).stem or "video_clip"
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in stem)
    return cleaned.strip("_") or "video_clip"


def _clip_output_path(source_path: str, event_number, start: float, stop: float | None) -> Path:
    ensure_data_dirs()
    start_label = int(max(0.0, float(start or 0.0)))
    stop_label = "end" if stop is None else int(max(0.0, float(stop)))
    filename = f"shot_{event_number}_{_safe_stem(source_path)}_{start_label}s-{stop_label}s.mp4"
    output = VIDEOS_DIR / filename
    counter = 2
    while output.exists():
        output = VIDEOS_DIR / f"shot_{event_number}_{_safe_stem(source_path)}_{start_label}s-{stop_label}s_{counter}.mp4"
        counter += 1
    return output


def _player_segment(player) -> dict | None:
    source_id = str(getattr(player, "video_source_id", None) or getattr(player, "video_path", "") or "")
    if not source_id:
        return None

    try:
        player.apply_segment_fields(normalize=True)
    except Exception:
        pass

    start = float(getattr(player, "start_time", DEFAULT_VIDEO_START) or DEFAULT_VIDEO_START)
    stop = getattr(player, "stop_time", None)
    stop = None if stop in ("", None) else float(stop)

    return {
        "source_id": source_id,
        "start": start,
        "stop": stop,
        "is_online": is_http_url(source_id),
    }


def _run_on_ui(app, callback, *args) -> None:
    root = getattr(app, "root", None)
    if root is not None:
        try:
            root.after(0, lambda: callback(*args))
            return
        except Exception:
            pass
    callback(*args)


def _refresh_after_video_update(app) -> None:
    try:
        app.refresh_all()
    except Exception:
        pass
    try:
        app.auto_update_current_match()
    except Exception:
        pass


def capture_video_segment_for_next_event(app, player) -> None:
    """Remember the current player segment so the next plotted event can link it."""

    segment = _player_segment(player)
    if segment is not None:
        setattr(app, PENDING_VIDEO_ATTR, segment)


def _fallback_video_dict(segment: dict) -> dict:
    return {
        "path": segment["source_id"],
        "start": segment.get("start", DEFAULT_VIDEO_START),
        "stop": segment.get("stop", None),
    }


def _clip_video_dict(exported_path: Path, start: float, stop: float | None) -> dict:
    clip_duration = None if stop is None else max(0.0, float(stop) - float(start or 0.0))
    return {"path": str(exported_path), "start": 0.0, "stop": clip_duration}


def _replace_event_video(app, match_name: str, latest_index: int, event_number, video_dict: dict) -> bool:
    logs = app.match_logs.get(match_name, [])
    if latest_index >= len(logs):
        return False

    entry = list(logs[latest_index])
    if entry and entry[0] != event_number:
        return False

    entry[IDX_VIDEO] = video_dict
    logs[latest_index] = tuple(entry)
    return True


def _start_async_clip_export(app, match_name: str, latest_index: int, event_number, segment: dict) -> None:
    source_id = segment["source_id"]
    start = float(segment.get("start") or DEFAULT_VIDEO_START)
    stop = segment.get("stop", None)
    output_path = _clip_output_path(source_id, event_number, start, stop)
    progress = show_render_progress(
        app,
        message="Saving shot and rendering the linked 1080p video clip...",
    )

    def progress_callback(fraction, rendered, total) -> None:
        _run_on_ui(app, update_render_progress, progress, fraction, rendered, total)

    def done_callback(exported, error) -> None:
        def finish() -> None:
            try:
                if error is not None:
                    if isinstance(error, VideoClipExportError):
                        title = "Clip Export Failed"
                        detail = "The shot was linked to the original video instead.\n\n" + str(error)
                    else:
                        title = "Video Link Warning"
                        detail = "The shot was linked to the original video, but the short clip could not be exported.\n\n" + str(error)
                    messagebox.showwarning(title, detail)
                    return

                if _replace_event_video(app, match_name, latest_index, event_number, _clip_video_dict(exported, start, stop)):
                    _refresh_after_video_update(app)
            finally:
                close_render_progress(progress)

        _run_on_ui(app, finish)

    export_local_segment_async(
        source_id,
        str(output_path),
        start=start,
        stop=stop,
        progress_callback=progress_callback,
        done_callback=done_callback,
    )


def attach_pending_video_to_latest_event(app) -> None:
    """Attach the captured video segment to the most recently created event."""

    segment = getattr(app, PENDING_VIDEO_ATTR, None)
    if not segment:
        return
    setattr(app, PENDING_VIDEO_ATTR, None)

    match_name = app.current_match.get()
    logs = app.match_logs.get(match_name, [])
    if not logs:
        return

    latest_index = len(logs) - 1
    entry = list(logs[latest_index])
    event_number = entry[0] if entry else latest_index + 1
    entry[IDX_VIDEO] = _fallback_video_dict(segment)
    logs[latest_index] = tuple(entry)

    source_id = segment["source_id"]
    stop = segment.get("stop", None)

    if segment.get("is_online") or not os.path.exists(source_id) or stop is None:
        return

    # Auto-linked exports must not block the Tk mainloop while FFmpeg renders.
    # Link the shot to the source immediately, then swap in the short MP4 when
    # the background export finishes.
    _start_async_clip_export(app, match_name, latest_index, event_number, segment)
