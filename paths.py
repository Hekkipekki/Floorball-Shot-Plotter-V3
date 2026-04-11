from pathlib import Path
import sys


def get_project_root() -> Path:
    """Return the project root folder."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    path = Path(__file__).resolve().parent
    while True:
        if (path / "main.py").exists():
            return path
        if path.parent == path:
            raise FileNotFoundError("Could not find project root containing main.py")
        path = path.parent


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
    for folder in (DATA_DIR, MATCHES_DIR, EXPORTS_DIR, VIDEOS_DIR):
        folder.mkdir(parents=True, exist_ok=True)