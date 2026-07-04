from core.entry_helpers import normalize_entry
from core.schema import IDX_VIDEO, ENTRY_LENGTH

DEFAULT_VIDEO_START = 0.0


def _normalized_video_dict(video):
    path = str(video.get("path") or "")
    if not path:
        return None

    start = float(video.get("start") or DEFAULT_VIDEO_START)
    stop = video.get("stop", None)
    stop = None if stop in ("", None) else float(stop)

    return {
        "path": path,
        "start": start,
        "stop": stop,
    }


def _normalized_legacy_video(video):
    path = str(video).strip()
    if not path:
        return None

    return {
        "path": path,
        "start": DEFAULT_VIDEO_START,
        "stop": None,
    }


def normalize_video(video):
    """
    Ensure we store video as:
      None OR {"path": str, "start": float, "stop": float|None}
    Accepts legacy string too.
    """
    if not video:
        return None

    if isinstance(video, dict):
        return _normalized_video_dict(video)

    return _normalized_legacy_video(video)


def serialize_entry(entry):
    """
    Returns a JSON-safe list length ENTRY_LENGTH.
    IDX_VIDEO is stored as dict or None.
    """
    entry = normalize_entry(entry)
    entry[IDX_VIDEO] = normalize_video(entry[IDX_VIDEO])
    return entry[:ENTRY_LENGTH]


def deserialize_entry(entry):
    """
    Returns a tuple length ENTRY_LENGTH.
    Upgrades legacy formats so IDX_VIDEO becomes dict/None.
    """
    entry = normalize_entry(entry)
    entry[IDX_VIDEO] = normalize_video(entry[IDX_VIDEO])
    return tuple(entry[:ENTRY_LENGTH])
