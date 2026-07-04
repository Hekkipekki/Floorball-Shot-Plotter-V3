"""VLC runtime bootstrap and small video-player helpers."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path

from paths import get_project_root

VLC_DIR_NAME = "vlc"
VLC_PLUGIN_DIR_NAME = "plugins"
LIBVLC_FILENAME = "libvlc.dll"
LIBVLCCORE_FILENAME = "libvlccore.dll"
MISSING_RUNTIME_MESSAGE = "⚠️ Bundled VLC runtime not found or incomplete."
INVALID_TIME_TEXT = "--:--"
TIME_SECONDS_MIN = 0


def _vlc_runtime_paths() -> tuple[Path, Path, Path, Path]:
    base = Path(get_project_root())
    vlc_dir = base / VLC_DIR_NAME
    plugins_dir = vlc_dir / VLC_PLUGIN_DIR_NAME
    libvlc_path = vlc_dir / LIBVLC_FILENAME
    libvlccore_path = vlc_dir / LIBVLCCORE_FILENAME
    return vlc_dir, plugins_dir, libvlc_path, libvlccore_path


def _has_complete_vlc_runtime(plugins_dir: Path, libvlc_path: Path, libvlccore_path: Path) -> bool:
    return libvlc_path.exists() and libvlccore_path.exists() and plugins_dir.exists()


def _configure_vlc_environment(vlc_dir: Path, plugins_dir: Path) -> None:
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(vlc_dir))

    os.environ["PATH"] = f"{vlc_dir};{os.environ.get('PATH', '')}"
    os.environ["VLC_PLUGIN_PATH"] = str(plugins_dir.resolve())


def _preload_vlc_dlls(libvlccore_path: Path, libvlc_path: Path) -> None:
    ctypes.CDLL(str(libvlccore_path.resolve()))
    ctypes.CDLL(str(libvlc_path.resolve()))


def configure_vlc_runtime() -> tuple[Path | None, Path | None]:
    vlc_dir, plugins_dir, libvlc_path, libvlccore_path = _vlc_runtime_paths()

    if not _has_complete_vlc_runtime(plugins_dir, libvlc_path, libvlccore_path):
        print(MISSING_RUNTIME_MESSAGE)
        return None, None

    try:
        _configure_vlc_environment(vlc_dir, plugins_dir)
        _preload_vlc_dlls(libvlccore_path, libvlc_path)
        return vlc_dir, plugins_dir

    except Exception as e:
        print(f"❌ Failed to preload bundled VLC DLLs: {e}")
        return None, None


def _coerce_seconds(seconds) -> int | None:
    try:
        return max(TIME_SECONDS_MIN, int(float(seconds)))
    except Exception:
        return None


def format_time(seconds: float | int | None) -> str:
    if seconds is None:
        return INVALID_TIME_TEXT

    seconds = _coerce_seconds(seconds)
    if seconds is None:
        return INVALID_TIME_TEXT

    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def parse_float(value: str, fallback: float | None = None) -> float | None:
    value = (value or "").strip().replace(",", ".")
    if value == "":
        return fallback

    try:
        return float(value)
    except ValueError:
        return fallback


VLC_DIR, PLUGINS_DIR = configure_vlc_runtime()

try:
    import vlc  # type: ignore

    VLC_IMPORT_ERROR: Exception | None = None
except Exception as e:
    vlc = None
    VLC_IMPORT_ERROR = e
