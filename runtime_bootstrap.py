from __future__ import annotations

import os
import sys
from pathlib import Path


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def configure_bundled_vlc() -> None:
    """Make python-vlc find the bundled Windows VLC runtime when present."""
    root = _app_root()
    vlc_dir = root / "vlc"
    plugins_dir = vlc_dir / "plugins"

    if not vlc_dir.exists():
        return

    os.environ.setdefault("VLC_PLUGIN_PATH", str(plugins_dir))

    if sys.platform.startswith("win"):
        try:
            os.add_dll_directory(str(vlc_dir))
        except Exception:
            pass

    path = os.environ.get("PATH", "")
    vlc_path = str(vlc_dir)
    if vlc_path.lower() not in path.lower():
        os.environ["PATH"] = vlc_path + os.pathsep + path
