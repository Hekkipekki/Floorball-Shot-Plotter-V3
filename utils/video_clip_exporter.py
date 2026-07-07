"""Export shorter local video clips from selected Start/Stop segments."""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path


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


def _run_ffmpeg(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


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
