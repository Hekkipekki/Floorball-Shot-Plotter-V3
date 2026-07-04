from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
from scipy.interpolate import LinearNDInterpolator

from app_paths import DATA_DIR

CALIBRATION_DONE_TEXT = "Calibration active: video clicks now use calibrated rink coordinates."
CALIBRATION_DIR = Path(DATA_DIR) / "calibrations"
CALIBRATION_STORE = CALIBRATION_DIR / "video_calibrations.json"

# Target plot coordinates are measured from the current defensive-half background image.
# Source coordinates are normalized video coordinates, so calibration survives window resizing.
GOPRO_CALIBRATION_POINTS = (
    ("Målområde lower-left corner", (566, 1033), "Click the lower-left corner of the large målområde rectangle."),
    ("Målområde lower-right corner", (910, 1034), "Click the lower-right corner of the large målområde rectangle."),
    ("Målområde upper-right corner", (909, 805), "Click the upper-right corner of the large målområde rectangle."),
    ("Målområde upper-left corner", (566, 802), "Click the upper-left corner of the large målområde rectangle."),
    ("Målvaktsområde lower-left corner", (644, 999), "Click the lower-left corner of the smaller målvaktsområde rectangle."),
    ("Målvaktsområde lower-right corner", (831, 1000), "Click the lower-right corner of the smaller målvaktsområde rectangle."),
    ("Målvaktsområde upper-right corner", (829, 930), "Click the upper-right corner of the smaller målvaktsområde rectangle."),
    ("Målvaktsområde upper-left corner", (645, 932), "Click the upper-left corner of the smaller målvaktsområde rectangle."),
    ("Defensive zone top-left", (21, 21), "Click the top-left defensive-zone board/rink reference."),
    ("Defensive zone top-right", (1434, 23), "Click the top-right defensive-zone board/rink reference."),
    ("Defensive zone top-middle", (734, 23), "Click the top-middle defensive-zone board/rink reference."),
    ("Defensive zone centre", (734, 500), "Click the centre of the defensive zone."),
    ("Left middle board", (21, 500), "Click the left board at about the middle of the defensive zone."),
    ("Right middle board", (1434, 500), "Click the right board at about the middle of the defensive zone."),
    ("Goal-line centre", (737, 1000), "Click the centre of the goal line / goal mouth."),
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
    data[_video_key(video_path)] = {"clicks": calibration_clicks}
    _write_store(data)


def load_video_calibration(video_path: str) -> list[dict]:
    data = _read_store()
    record = data.get(_video_key(video_path), {})
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
