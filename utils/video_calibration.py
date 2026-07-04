from __future__ import annotations

import numpy as np

CALIBRATION_DONE_TEXT = "Calibration active: video clicks now use calibrated rink coordinates."

# Target plot coordinates use the current 1500 x 1000 defensive-half rink template.
# Source coordinates are normalized video coordinates, so calibration survives window resizing.
GOPRO_CALIBRATION_POINTS = (
    ("Målområde lower-left corner", (562, 825), "Click the lower-left corner of the large målområde rectangle."),
    ("Målområde lower-right corner", (938, 825), "Click the lower-right corner of the large målområde rectangle."),
    ("Målområde upper-right corner", (938, 625), "Click the upper-right corner of the large målområde rectangle."),
    ("Målområde upper-left corner", (562, 625), "Click the upper-left corner of the large målområde rectangle."),
    ("Målvaktsområde lower-left corner", (656, 825), "Click the lower-left corner of the smaller målvaktsområde rectangle."),
    ("Målvaktsområde lower-right corner", (844, 825), "Click the lower-right corner of the smaller målvaktsområde rectangle."),
    ("Målvaktsområde upper-right corner", (844, 775), "Click the upper-right corner of the smaller målvaktsområde rectangle."),
    ("Målvaktsområde upper-left corner", (656, 775), "Click the upper-left corner of the smaller målvaktsområde rectangle."),
    ("Defensive zone top-left", (0, 0), "Click the top-left defensive-zone board/rink reference."),
    ("Defensive zone top-right", (1500, 0), "Click the top-right defensive-zone board/rink reference."),
    ("Defensive zone top-middle", (750, 0), "Click the top-middle defensive-zone board/rink reference."),
    ("Defensive zone centre", (750, 500), "Click the centre of the defensive zone."),
    ("Left middle board", (0, 500), "Click the left board at about the middle of the defensive zone."),
    ("Right middle board", (1500, 500), "Click the right board at about the middle of the defensive zone."),
)


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
