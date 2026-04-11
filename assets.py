from __future__ import annotations

import os
from typing import List

from paths import get_project_root


ASSETS_DIR = os.path.join(get_project_root(), "assets")
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, "backgrounds")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
RESOURCES_DIR = os.path.join(ASSETS_DIR, "resources")


def get_asset_path(*parts: str) -> str:
    return os.path.join(ASSETS_DIR, *parts)


def get_background_path(filename: str) -> str:
    return os.path.join(BACKGROUNDS_DIR, filename)


def get_icon_path(filename: str) -> str:
    return os.path.join(ICONS_DIR, filename)


def get_resource_path(*parts: str) -> str:
    return os.path.join(RESOURCES_DIR, *parts)


def list_background_files() -> List[str]:
    if not os.path.isdir(BACKGROUNDS_DIR):
        return []

    valid_exts = (".png", ".jpg", ".jpeg", ".webp")
    return sorted(
        f for f in os.listdir(BACKGROUNDS_DIR)
        if f.lower().endswith(valid_exts)
    )


def get_default_background() -> str:
    files = list_background_files()
    return files[0] if files else ""