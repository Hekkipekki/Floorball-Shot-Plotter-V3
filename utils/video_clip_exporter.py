"""Export shorter local video clips from selected Start/Stop segments."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class VideoClipExportError(RuntimeError):
    """Raised when a segment cannot be exported."""


def _find_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        return ffmpeg
    raise VideoClipExportError(
        "FFmpeg is required to export shorter clips. Install FFmpeg and make sure ffmpeg.exe is available on PATH."
    )


def _duration(start: float, stop: float | None) -> float | None:
    if stop is None:
        return None
    length = float(stop) - float(start or 0.0)
    if length <= 0:
        raise VideoClipExportError("Stop time must be after Start time before exporting a clip.")
    return length


def _run_ffmpeg(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def export_local_segment(source_path: str, output_path: str, start: float = 0.0, stop: float | None = None) -> Path:
    """Export a local video segment to output_path and return the output Path."""

    source = Path(source_path).expanduser()
    output = Path(output_path).expanduser()

    if not source.exists():
        raise VideoClipExportError("Source video file could not be found.")
    if source.resolve() == output.resolve():
        raise VideoClipExportError("Choose a different output file than the source video.")

    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = _find_ffmpeg()
    start = max(0.0, float(start or 0.0))
    length = _duration(start, stop)

    base_command = [ffmpeg, "-y", "-ss", f"{start:.3f}", "-i", str(source)]
    if length is not None:
        base_command += ["-t", f"{length:.3f}"]

    # First try stream copy for speed and zero generation loss. If the source
    # codec/container does not allow that cut, fall back to a reliable re-encode.
    copy_command = base_command + ["-c", "copy", "-avoid_negative_ts", "make_zero", str(output)]
    result = _run_ffmpeg(copy_command)
    if result.returncode == 0 and output.exists() and output.stat().st_size > 0:
        return output

    encode_command = base_command + [
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(output),
    ]
    result = _run_ffmpeg(encode_command)
    if result.returncode == 0 and output.exists() and output.stat().st_size > 0:
        return output

    details = (result.stderr or result.stdout or "Unknown FFmpeg error").strip()
    raise VideoClipExportError(f"Could not export clip:\n{details[-1200:]}")
