from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR      = PROJECT_ROOT / "data"
RAW_DIR       = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
LOGS_DIR      = PROJECT_ROOT / "logs"
BACKUPS_DIR   = PROJECT_ROOT / "backups"
OUTPUT_DIR    = PROJECT_ROOT / "output"

LOG_FILE = LOGS_DIR / "project.log"