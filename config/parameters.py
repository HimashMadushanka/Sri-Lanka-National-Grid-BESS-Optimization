"""
Configuration parameters loader for the Sri Lanka Grid BESS Optimization project.
"""
import json
from pathlib import Path
from src.paths import CONFIG

CONFIG_PATH = CONFIG / "model_config.json"


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Load model parameters from the JSON configuration file."""
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Pre-loaded configuration constants
try:
    CONFIG_DATA = load_config()
    BATTERY_PARAMS = CONFIG_DATA.get("battery", {})
    OPTIMIZATION_PARAMS = CONFIG_DATA.get("optimization", {})
    GRAPH_PARAMS = CONFIG_DATA.get("graph", {})
except Exception:
    CONFIG_DATA = {}
    BATTERY_PARAMS = {}
    OPTIMIZATION_PARAMS = {}
    GRAPH_PARAMS = {}
