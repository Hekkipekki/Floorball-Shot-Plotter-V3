"""Export shorter local video clips from selected Start/Stop segments."""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable


class VideoClipExportError(RuntimeError):
    """Raised when a segment cannot be exported."""


COMMON_FFMPEG_PATHS = (
    r"C:\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
)

WINGET_FFMPEG_GLOBS = (
    r"%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe",
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*FFmpeg*\**\ffmpeg.exe",
    r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*Gyan*FFmpeg*\**\ffmpeg.exe",
    r"%USERPROFILE%\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe",
    r"%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\*FFmpeg*\**\ffmpeg.exe",
    r"%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\*Gyan*FFmpeg*\**\ffmpeg.exe",
)

ANALYSIS_CRF = "24"
AUDIO_BITRATE = "128k"
MAX_EXPORT_HEIGHT = 1080
ProgressCallback = Callable[[float | None, float | None, float | None], None]


def _candidate_paths_from_path_env() -> list[str]:
    candidates: list[str] = []
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        folder = folder.strip().strip('"')
        if not folder:
            continue
        candidate = Path(folder) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
        candidates.append(str(candidate))
    return candidates


def _candidate_paths_from_windows_where() -> list[str]:
    if os.name != "nt":
        return []
    candidates: list[str] = []
    commands = (["where", "ffmpeg"], ["cmd", "/c", "where ffmpeg"])
    for command in commands:
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception:
            continue
        if result.returncode == 0:
            candidates.extend(line.strip() for line in result.stdout.splitlines() if line.strip())
    return candidates


def _candidate_paths_from_winget_dirs() -> list[str]:
    candidates: list[str] = []
    if os.name != "nt":
        return candidates
    for pattern in WINGET_FFMPEG_GLOBS:
        expanded = os.path.expandvars(pattern)
        candidates.extend(glob.glob(expanded, recursive=True))
    return candidates


def _is_usable_ffmpeg(command: str) -> bool:
    try:
        result = subprocess.run(
            [command, "-version"],
            capture_output=True,
            text=True,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return result.returncode == 0
    except Exception:
        return False


def _find_ffmpeg() -> str:
    candidates: list[str] = []

    found = shutil.which("ffmpeg") or shutil.which("ffmpeg.exe")
    if found:
        candidates.append(found)

    candidates.append("ffmpeg")
    if os.name == "nt":
        candidates.append("ffmpeg.exe")

    candidates.extend(COMMON_FFMPEG_PATHS)
    candidates.extend(_candidate_paths_from_path_env())
    candidates.extend(_candidate_paths_from_windows_where())
    candidates.extend(_candidate_paths_from_winget_dirs())

    try:
        candidates.append(str(Path(sys.executable).resolve().parent / "ffmpeg.exe"))
    except Exception:
        pass
    try:
        candidates.append(str(Path(__file__).resolve().parents[1] / "ffmpeg.exe"))
    except Exception:
        pass

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if candidate not in {"ffmpeg", "ffmpeg.exe"} and not Path(candidate).exists():
            continue
        if _is_usable_ffmpeg(candidate):
            return candidate

    raise VideoClipExportError(
        "FFmpeg is required to export shorter clips, but the app could not find ffmpeg.exe.\n\n"
        "PowerShell can see FFmpeg, so it is probably installed in a location the packaged app cannot inherit.\n\n"
        "Fast fix: run `where ffmpeg` in PowerShell, then copy that ffmpeg.exe next to Floorball Shot Plotter.exe "
        "or into C:\\ffmpeg\\bin."
    )


def _duration(start: float, stop: float | None) -> float | None:
    if stop is None:
        return None
    length = float(stop) - float(start or 0.0)
    if length <= 0:
        raise VideoClipExportError("Stop time must be after Start time before exporting a clip.")
    return length


def _parse_progress_seconds(value: str) -> float | None:
    try:
        return max(0.0, int(value) / 1_000_000)
    except Exception:
        return None


def _run_ffmpeg_with_progress(command: list[str], duration: float | None, progress_callback: ProgressCallback | None = None) -> subprocess.CompletedProcess[str]:
    progress_command = command[:-1] + ["-progress", "pipe:1", "-nostats", command[-1]]
    process = subprocess.Popen(
        progress_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    last_seconds = 0.0
    if progress_callback:
        progress_callback(0.0 if duration else None, 0.0, duration)

    stdout_lines: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        stdout_lines.append(line)
        key, _, value = line.strip().partition("=")
        if key == "out_time_ms":
            seconds = _parse_progress_seconds(value)
            if seconds is not None:
                last_seconds = seconds
                fraction = None if not duration else min(1.0, seconds / duration)
                if progress_callback:
                    progress_callback(fraction, seconds, duration)

    stderr = process.stderr.read() if process.stderr is not None else ""
    return_code = process.wait()
    if progress_callback:
        progress_callback(1.0 if return_code == 0 else None, last_seconds, duration)

    return subprocess.CompletedProcess(progress_command, return_code, "".join(stdout_lines), stderr)


def _build_analysis_export_command(ffmpeg: str, source: Path, output: Path, start: float, length: float | None) -> list[str]:
    command = [ffmpeg, "-y", "-ss", f"{start:.3f}", "-i", str(source)]
    if length is not None:
        command += ["-t", f"{length:.3f}"]
    command += [
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        f"scale='min(iw,-2)':'min(ih,{MAX_EXPORT_HEIGHT})':force_original_aspect_ratio=decrease",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        ANALYSIS_CRF,
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        AUDIO_BITRATE,
        "-movflags",
        "+faststart",
        str(output),
    ]
    return command


def export_local_segment(
    source_path: str,
    output_path: str,
    start: float = 0.0,
    stop: float | None = None,
    progress_callback: ProgressCallback | None = None,
) -> Path:
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

    command = _build_analysis_export_command(ffmpeg, source, output, start, length)
    result = _run_ffmpeg_with_progress(command, length, progress_callback)
    if result.returncode == 0 and output.exists() and output.stat().st_size > 0:
        return output

    details = (result.stderr or result.stdout or "Unknown FFmpeg error").strip()
    raise VideoClipExportError(f"Could not export clip:\n{details[-1200:]}")
