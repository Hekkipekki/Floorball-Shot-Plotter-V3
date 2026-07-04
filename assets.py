from __future__ import annotations

import os
from typing import List

from paths import ASSETS_DIR, BACKGROUNDS_DIR, ICONS_DIR

RESOURCES_DIR = ASSETS_DIR / "resources"
VALID_BACKGROUND_EXTS = (".png", ".jpg", ".jpeg", ".webp")


def _as_str(path) -> str:
    return str(path)


def get_asset_path(*parts: str) -> str:
    return _as_str(ASSETS_DIR.joinpath(*parts))


def get_background_path(filename: str) -> str:
    return _as_str(BACKGROUNDS_DIR / filename)


def get_icon_path(filename: str) -> str:
    return _as_str(ICONS_DIR / filename)


def get_resource_path(*parts: str) -> str:
    return _as_str(RESOURCES_DIR.joinpath(*parts))


def list_background_files() -> List[str]:
    if not BACKGROUNDS_DIR.is_dir():
        return []

    return sorted(
        filename for filename in os.listdir(BACKGROUNDS_DIR)
        if filename.lower().endswith(VALID_BACKGROUND_EXTS)
    )


def get_default_background() -> str:
    files = list_background_files()
    return files[0] if files else ""
