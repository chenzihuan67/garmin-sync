from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_DIR = PROJECT_ROOT / "database"
DATABASE_PATH = DATABASE_DIR / "garmin.db"
SUMMARY_CSV_PATH = PROJECT_ROOT / "summary.csv"
