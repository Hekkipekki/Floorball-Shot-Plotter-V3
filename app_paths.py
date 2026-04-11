from __future__ import annotations

import os

from paths import get_project_root


PROJECT_ROOT = get_project_root()

ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MATCHES_DIR = os.path.join(DATA_DIR, "matches")
CSV_DATA_DIR = os.path.join(PROJECT_ROOT, "csv_data")