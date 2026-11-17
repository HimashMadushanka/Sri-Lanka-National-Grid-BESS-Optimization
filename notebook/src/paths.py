from pathlib import Path
import sys

def _find_project_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current, *current.parents]:
        if (parent / "datasets").is_dir() and (parent / "notebook").is_dir():
            return parent
    return current.parents[1]

ROOT = _find_project_root(Path(__file__))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA = ROOT / "datasets"

RAW = DATA / "raw"

PROCESSED = DATA / "processed"
TEMPLATES = DATA / "templates"

OFFICIAL = RAW / "official_report_csv"
GIS = RAW / "gis"
SOLAR = RAW / "solar"
NASA = SOLAR / "nasa_power_hourly"
ELECTRICITY = RAW / "electricity"

NOTEBOOKS = ROOT / "notebook"
CONFIG = ROOT / "config"

RESULTS = ROOT / "results"
GRAPHS = RESULTS / "graphs"
MAPS = RESULTS / "maps"
OPTIMIZATION = RESULTS / "optimization"
SENSITIVITY = RESULTS / "sensitivity"
TABLES = RESULTS / "tables"

def create_project_directories():
    folders = [
        OFFICIAL, GIS, SOLAR, NASA, ELECTRICITY,
        PROCESSED, TEMPLATES, GRAPHS, MAPS,
        OPTIMIZATION, SENSITIVITY, TABLES
    ]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    print("Project directories are ready.")

if __name__ == "__main__":
    create_project_directories()
