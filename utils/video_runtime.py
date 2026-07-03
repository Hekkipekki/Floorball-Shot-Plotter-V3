"""VLC runtime bootstrap and small video-player helpers."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path

from paths import get_project_root


def configure_vlc_runtime() -> tuple[Path | None, Path | None]:
    base = Path(get_project_root())
    vlc_dir = base / "vlc"
    plugins_dir = vlc_dir / "plugins"
    libvlc_path = vlc_dir / "libvlc.dll"
    libvlccore_path = vlc_dir / "libvlccore.dll"

    if not libvlc_path.exists() or not libvlccore_path.exists() or not plugins_dir.exists():
        print("⚠️ Bundled VLC runtime not found or incomplete.")
        return None, None

    try:
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(vlc_dir))

        os.environ["PATH"] = f"{vlc_dir};{os.environ.get('PATH', '')}"
        os.environ["VLC_PLUGIN_PATH"] = str(plugins_dir.resolve())

        ctypes.CDLL(str(libvlccore_path.resolve()))
        ctypes.CDLL(str(libvlc_path.resolve()))

        return vlc_dir, plugins_dir

    except Exception as e:
        print(f"❌ Failed to preload bundled VLC DLLs: {e}")
        return None, None


def format_time(seconds: float | int | None) -> str:
    if seconds is None:
        return "--:--"

    try:
        seconds = max(0, int(float(seconds)))
    except Exception:
        return "--:--"

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
