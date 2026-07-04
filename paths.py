from pathlib import Path
import sys

PROJECT_MARKER_FILE = "main.py"
DATA_SUBDIRS = ("matches", "exports", "videos")


def _is_frozen_app() -> bool:
    return bool(getattr(sys, "frozen", False))


def _frozen_project_root() -> Path:
    return Path(sys.executable).resolve().parent


def _source_project_root() -> Path:
    path = Path(__file__).resolve().parent
    while True:
        if (path / PROJECT_MARKER_FILE).exists():
            return path
        if path.parent == path:
            raise FileNotFoundError(f"Could not find project root containing {PROJECT_MARKER_FILE}")
        path = path.parent


def get_project_root() -> Path:
    """Return the project root folder."""
    if _is_frozen_app():
        return _frozen_project_root()
    return _source_project_root()


PROJECT_ROOT = get_project_root()

CORE_DIR = PROJECT_ROOT / "core"
GUI_DIR = PROJECT_ROOT / "gui"
UTILS_DIR = PROJECT_ROOT / "utils"
CONFIG_DIR = PROJECT_ROOT / "config"

ASSETS_DIR = PROJECT_ROOT / "assets"
DATA_DIR = PROJECT_ROOT / "data"

MATCHES_DIR = DATA_DIR / "matches"
EXPORTS_DIR = DATA_DIR / "exports"
VIDEOS_DIR = DATA_DIR / "videos"

IMAGES_DIR = ASSETS_DIR / "images"
ICONS_DIR = ASSETS_DIR / "icons"
BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"


def ensure_data_dirs() -> None:
    """Create runtime data folders if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for folder_name in DATA_SUBDIRS:
        (DATA_DIR / folder_name).mkdir(parents=True, exist_ok=True)
