"""
Задание 3 (часть 1): архивирование data/ в backups/backup_YYYYMMDD.zip.
Внутри архива сохраняется относительная структура: data/raw/..., data/processed/...
"""
import logging
import zipfile
from datetime import datetime
from pathlib import Path

from config import BACKUPS_DIR, DATA_DIR, LOG_FILE


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("project")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    return logger


def make_backup(logger: logging.Logger) -> Path:
    """
    Создаёт zip-архив всей директории data/ (рекурсивно).
    Имя: backup_<YYYYMMDD>.zip в BACKUPS_DIR.
    """
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    archive_path = BACKUPS_DIR / f"backup_{today}.zip"

    files = [p for p in DATA_DIR.rglob("*") if p.is_file()]
    if not files:
        logger.error("В %s нет файлов — архивировать нечего.", DATA_DIR)
        return archive_path

    if archive_path.exists():
        logger.warning("Архив %s уже существует — перезаписываем.", archive_path.name)

    with zipfile.ZipFile(
        archive_path, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zf:
        for path in files:
            arcname = path.relative_to(DATA_DIR.parent).as_posix()
            zf.write(path, arcname=arcname)
            logger.info("Добавлен в архив: %s", arcname)

    size = archive_path.stat().st_size
    logger.info(
        "Архив создан: %s (%d файлов, %d байт)",
        archive_path.name, len(files), size,
    )
    return archive_path


def run() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 3 (часть 1): %s", datetime.now().isoformat(timespec="seconds"))
    archive = make_backup(logger)
    logger.info("Задание 3 (часть 1) завершено: %s", archive)
    logger.info("=" * 60)


run()