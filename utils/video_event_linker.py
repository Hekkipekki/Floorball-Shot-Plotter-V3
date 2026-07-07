"""Link video-player segments to shots/goals created from video plotting."""

from __future__ import annotations

import os
from pathlib import Path
from tkinter import messagebox

from core.schema import IDX_VIDEO
from paths import VIDEOS_DIR, ensure_data_dirs
from utils.render_progress import close_render_progress, show_render_progress
from utils.video_clip_exporter import VideoClipExportError, export_local_segment
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


def capture_video_segment_for_next_event(app, player) -> None:
    """Remember the current player segment so the next plotted event can link it."""

    segment = _player_segment(player)
    if segment is not None:
        setattr(app, PENDING_VIDEO_ATTR, segment)


def _video_dict_for_segment(app, segment: dict, event_number) -> dict:
    source_id = segment["source_id"]
    start = float(segment.get("start") or DEFAULT_VIDEO_START)
    stop = segment.get("stop", None)

    if segment.get("is_online"):
        return {"path": source_id, "start": start, "stop": stop}

    if not os.path.exists(source_id):
        return {"path": source_id, "start": start, "stop": stop}

    # With a Stop time, create a real short clip and link that. Without Stop,
    # keep the source video plus the saved Start value so users do not
    # accidentally export the rest of a full match.
    if stop is None:
        return {"path": source_id, "start": start, "stop": None}

    output_path = _clip_output_path(source_id, event_number, start, stop)
    progress = show_render_progress(
        app,
        message="Saving shot and rendering the linked video clip...\nThis can take a little while for 4K video.",
    )
    try:
        exported = export_local_segment(source_id, str(output_path), start=start, stop=stop)
    finally:
        close_render_progress(progress)
    clip_duration = max(0.0, float(stop) - start)
    return {"path": str(exported), "start": 0.0, "stop": clip_duration}


def attach_pending_video_to_latest_event(app) -> None:
    """Attach the captured video segment to the most recently created event."""

    segment = getattr(app, PENDING_VIDEO_ATTR, None)
    if not segment:
        return
    setattr(app, PENDING_VIDEO_ATTR, None)

    logs = app.match_logs.get(app.current_match.get(), [])
    if not logs:
        return

    latest_index = len(logs) - 1
    entry = list(logs[latest_index])
    event_number = entry[0] if entry else latest_index + 1

    try:
        entry[IDX_VIDEO] = _video_dict_for_segment(app, segment, event_number)
    except VideoClipExportError as exc:
        entry[IDX_VIDEO] = {
            "path": segment["source_id"],
            "start": segment.get("start", DEFAULT_VIDEO_START),
            "stop": segment.get("stop", None),
        }
        messagebox.showwarning(
            "Clip Export Failed",
            "The shot was linked to the original video instead.\n\n" + str(exc),
        )
    except Exception as exc:
        entry[IDX_VIDEO] = {
            "path": segment["source_id"],
            "start": segment.get("start", DEFAULT_VIDEO_START),
            "stop": segment.get("stop", None),
        }
        messagebox.showwarning(
            "Video Link Warning",
            "The shot was linked to the original video, but the short clip could not be exported.\n\n" + str(exc),
        )

    logs[latest_index] = tuple(entry)
