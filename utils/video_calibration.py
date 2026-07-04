from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

from app_paths import DATA_DIR

CALIBRATION_DONE_TEXT = "Calibration active: video clicks now use calibrated rink coordinates."
CALIBRATION_VERSION = 3
CALIBRATION_DIR = Path(DATA_DIR) / "calibrations"
CALIBRATION_STORE = CALIBRATION_DIR / "video_calibrations.json"

# Target plot coordinates are measured from the current defensive-half background image.
# Source coordinates are normalized video coordinates, so calibration survives window resizing.
# Keep this preset tight: these are the mandatory/most useful anchors when visible.
GOPRO_CALIBRATION_POINTS = (
    ("1 Lower Left Goal Area", (562, 1033), "Click lower-left corner of the large goal area / målområde."),
    ("2 Lower Right Goal Area", (914, 1034), "Click lower-right corner of the large goal area / målområde."),
    ("3 Upper Right Goal Area", (913, 798), "Click upper-right corner of the large goal area / målområde."),
    ("4 Upper Left Goal Area", (563, 796), "Click upper-left corner of the large goal area / målområde."),
    ("5 Lower Left Goalie Area", (642, 999), "Click lower-left corner of the small goalie area / målvaktsområde."),
    ("6 Lower Right Goalie Area", (835, 999), "Click lower-right corner of the small goalie area / målvaktsområde."),
    ("7 Upper Left Goalie Area", (647, 930), "Click upper-left corner of the small goalie area / målvaktsområde."),
    ("8 Upper Right Goalie Area", (832, 930), "Click upper-right corner of the small goalie area / målvaktsområde."),
    ("9 Center of Goal Line", (740, 990), "Click the centre of the goal line / goal mouth."),
    ("10 Upper Left Defensive Zone", (18, 20), "Click the upper-left defensive-zone board/rink reference."),
    ("11 Upper Right Defensive Zone", (1431, 20), "Click the upper-right defensive-zone board/rink reference."),
    ("12 Center Faceoff Dot", (729, 19), "Click the visible centre/upper faceoff-dot reference."),
    ("13 Center of Defensive Zone", (730, 479), "Click the centre of the defensive zone."),
    ("14 Left Center Defensive Zone", (14, 481), "Click the left-board centre reference of the defensive zone."),
    ("15 Right Center Defensive Zone", (1437, 470), "Click the right-board centre reference of the defensive zone."),
    ("16 Lower Left Faceoff Dot", (99, 1018), "Click the lower-left faceoff-dot/circle reference."),
    ("17 Lower Right Faceoff Dot", (1350, 1022), "Click the lower-right faceoff-dot/circle reference."),
    ("18 Behind Goal Near Board", (744, 1204), "Click the centre point behind the goal near the end board."),
)


def _video_key(video_path: str) -> str:
    return os.path.abspath(video_path)


def _read_store() -> dict:
    try:
        if CALIBRATION_STORE.exists():
            return json.loads(CALIBRATION_STORE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _write_store(data: dict) -> None:
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
    CALIBRATION_STORE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_video_calibration(video_path: str, calibration_clicks: list[dict]) -> None:
    data = _read_store()
    data[_video_key(video_path)] = {
        "version": CALIBRATION_VERSION,
        "clicks": calibration_clicks,
    }
    _write_store(data)


def load_video_calibration(video_path: str) -> list[dict]:
    data = _read_store()
    record = data.get(_video_key(video_path), {})
    if record.get("version") != CALIBRATION_VERSION:
        return []
    clicks = record.get("clicks", [])
    return clicks if isinstance(clicks, list) else []


def compute_homography(calibration_clicks: list[dict]) -> np.ndarray | None:
    pairs = [click for click in calibration_clicks if "source_norm" in click and "target_plot" in click]
    if len(pairs) < 4:
        return None

    rows = []
    for click in pairs:
        src_x, src_y = click["source_norm"]
        dst_x, dst_y = click["target_plot"]
        rows.append([-src_x, -src_y, -1.0, 0.0, 0.0, 0.0, src_x * dst_x, src_y * dst_x, dst_x])
        rows.append([0.0, 0.0, 0.0, -src_x, -src_y, -1.0, src_x * dst_y, src_y * dst_y, dst_y])

    matrix = np.asarray(rows, dtype=float)
    try:
        _u, _s, vh = np.linalg.svd(matrix)
        homography = vh[-1].reshape(3, 3)
        if abs(homography[2, 2]) > 1e-9:
            homography = homography / homography[2, 2]
        return homography
    except Exception:
        return None


def _build_interpolators(calibration_clicks: list[dict]):
    pairs = [click for click in calibration_clicks if "source_norm" in click and "target_plot" in click]
    if len(pairs) < 3:
        return None, None

    source = np.asarray([click["source_norm"] for click in pairs], dtype=float)
    target_x = np.asarray([click["target_plot"][0] for click in pairs], dtype=float)
    target_y = np.asarray([click["target_plot"][1] for click in pairs], dtype=float)

    try:
        return LinearNDInterpolator(source, target_x), LinearNDInterpolator(source, target_y)
    except Exception:
        return None, None


def build_calibration_model(calibration_clicks: list[dict]) -> dict:
    interp_x, interp_y = _build_interpolators(calibration_clicks)
    return {
        "clicks": calibration_clicks,
        "homography": compute_homography(calibration_clicks),
        "interp_x": interp_x,
        "interp_y": interp_y,
    }


def apply_homography(homography: np.ndarray | None, source_norm: tuple[float, float]) -> tuple[int, int] | None:
    if homography is None:
        return None

    src_x, src_y = source_norm
    vector = np.asarray([src_x, src_y, 1.0], dtype=float)
    mapped = homography @ vector
    if abs(mapped[2]) <= 1e-9:
        return None

    plot_x = mapped[0] / mapped[2]
    plot_y = mapped[1] / mapped[2]
    return int(round(plot_x)), int(round(plot_y))


def apply_calibration_model(model: dict | None, source_norm: tuple[float, float]) -> tuple[int, int] | None:
    if not model:
        return None

    interp_x = model.get("interp_x")
    interp_y = model.get("interp_y")
    if interp_x is not None and interp_y is not None:
        try:
            mapped_x = float(interp_x(source_norm[0], source_norm[1]))
            mapped_y = float(interp_y(source_norm[0], source_norm[1]))
            if np.isfinite(mapped_x) and np.isfinite(mapped_y):
                return int(round(mapped_x)), int(round(mapped_y))
        except Exception:
            pass

    return apply_homography(model.get("homography"), source_norm)
