
from pathlib import Path
import re

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TERRAIN_DIR = PROJECT_ROOT / "data" / "terrain"


def get_terrain_file(scenario):
    """
    Find a terrain horizon CSV matching Awang's site code.
    """

    site_code = getattr(scenario, "site_code", None)

    if not site_code:
        return None

    # Restrict filenames to valid site-code characters.
    if not re.fullmatch(r"[A-Za-z0-9_-]+", site_code):
        raise ValueError("Invalid landing site code.")

    path = TERRAIN_DIR / f"{site_code}_horizon.csv"

    if path.is_file():
        return path

    return None


def load_site_terrain(scenario):
    """
    Load a processed terrain horizon CSV.

    The CSV must be generated from actual lunar
    elevation data and validated for this site.
    """

    path = get_terrain_file(scenario)

    if path is None:
        return None

    return pd.read_csv(path)
