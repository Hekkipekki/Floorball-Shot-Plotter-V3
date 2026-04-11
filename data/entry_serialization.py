from core.schema import IDX_VIDEO, ENTRY_LENGTH


def normalize_video(video):
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

        return {
            "path": path,
            "start": start,
            "stop": stop,
        }

    s = str(video).strip()
    if not s:
        return None

    return {
        "path": s,
        "start": 0.0,
        "stop": None,
    }


def serialize_entry(entry):
    """
    Returns a JSON-safe list length ENTRY_LENGTH.
    IDX_VIDEO is stored as dict or None.
    """
    entry = list(entry) + [None] * (ENTRY_LENGTH - len(entry))
    entry[IDX_VIDEO] = normalize_video(entry[IDX_VIDEO])
    return entry[:ENTRY_LENGTH]


def deserialize_entry(entry):
    """
    Returns a tuple length ENTRY_LENGTH.
    Upgrades legacy formats so IDX_VIDEO becomes dict/None.
    """
    entry = list(entry) + [None] * (ENTRY_LENGTH - len(entry))
    entry[IDX_VIDEO] = normalize_video(entry[IDX_VIDEO])
    return tuple(entry[:ENTRY_LENGTH])