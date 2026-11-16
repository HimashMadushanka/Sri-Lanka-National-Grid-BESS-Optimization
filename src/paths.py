from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "datasets"

RAW = DATA / "raw"

PROCESSED = DATA / "processed"
TEMPLATES = DATA / "templates"

OFFICIAL = RAW / "official_report_csv"
if not OFFICIAL.exists() or not any(OFFICIAL.glob("*.csv")):
    _alt_official = RAW / "data" / "raw" / "official_report_csv"
    if _alt_official.exists() and any(_alt_official.glob("*.csv")):
        OFFICIAL = _alt_official
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
