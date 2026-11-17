"""
Задание 3 (часть 2): восстановление data/ из архива + проверка целостности.

Логика:
1. Найти самый свежий backup_*.zip в backups/.
2. Распаковать в data_restored/ (отдельная директория, чтобы не затирать текущее data/).
3. Сравнить содержимое data/ и data_restored/data/ побайтово.
4. Записать результат проверки в лог.
"""
import hashlib
import logging
import zipfile
from datetime import datetime
from pathlib import Path

from config import BACKUPS_DIR, DATA_DIR, LOG_FILE, PROJECT_ROOT

RESTORE_DIR = PROJECT_ROOT / "data_restored"


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


def find_latest_backup(logger: logging.Logger) -> Path | None:
    """Возвращает самый свежий backup_*.zip (по mtime)."""
    archives = sorted(
        BACKUPS_DIR.glob("backup_*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not archives:
        logger.error("В %s нет архивов backup_*.zip.", BACKUPS_DIR)
        return None
    latest = archives[0]
    logger.info("Выбран архив для восстановления: %s", latest.name)
    return latest


def extract_archive(archive: Path, logger: logging.Logger) -> None:
    """Распаковывает архив в RESTORE_DIR, предварительно очищая её."""
    if RESTORE_DIR.exists():
        import shutil
        shutil.rmtree(RESTORE_DIR)
        logger.info("Очищена директория восстановления: %s", RESTORE_DIR)
    RESTORE_DIR.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, mode="r") as zf:
        # Проверка CRC каждого файла — встроенная в zipfile
        bad = zf.testzip()
        if bad is not None:
            logger.error("Архив повреждён, первый битый файл: %s", bad)
            raise zipfile.BadZipFile(f"CRC mismatch: {bad}")
        logger.info("CRC-проверка архива пройдена.")

        zf.extractall(RESTORE_DIR)
        logger.info(
            "Архив распакован в %s (%d файлов)",
            RESTORE_DIR, len(zf.namelist()),
        )


def file_sha256(path: Path) -> str:
    """SHA-256 содержимого файла — для побайтового сравнения."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compare_trees(source: Path, restored: Path, logger: logging.Logger) -> bool:
    """
    Сравнивает деревья source и restored по относительным путям и хэшам.
    Возвращает True, если всё совпадает.
    """
    src_files = {
        p.relative_to(source): p for p in source.rglob("*") if p.is_file()
    }
    rst_files = {
        p.relative_to(restored): p for p in restored.rglob("*") if p.is_file()
    }

    only_src = set(src_files) - set(rst_files)
    only_rst = set(rst_files) - set(src_files)
    common = set(src_files) & set(rst_files)

    ok = True
    for rel in sorted(only_src):
        logger.error("Файл есть в исходнике, но отсутствует в восстановленном: %s", rel)
        ok = False
    for rel in sorted(only_rst):
        logger.error("Лишний файл в восстановленном: %s", rel)
        ok = False

    for rel in sorted(common):
        h_src = file_sha256(src_files[rel])
        h_rst = file_sha256(rst_files[rel])
        if h_src != h_rst:
            logger.error("Несовпадение хэша: %s (src=%s, rst=%s)", rel, h_src[:12], h_rst[:12])
            ok = False
        else:
            logger.info("OK: %s (sha256=%s…)", rel, h_src[:12])

    if ok:
        logger.info(
            "Целостность подтверждена: %d файлов совпадают побайтово.", len(common)
        )
    else:
        logger.error("Обнаружены расхождения при сравнении деревьев.")
    return ok


def run() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 3 (часть 2): %s", datetime.now().isoformat(timespec="seconds"))

    archive = find_latest_backup(logger)
    if archive is None:
        return

    try:
        extract_archive(archive, logger)
    except zipfile.BadZipFile as e:
        logger.error("Не удалось восстановить архив: %s", e)
        return

    # data/ внутри архива лежит как data_restored/data/...
    restored_data = RESTORE_DIR / "data"
    if not restored_data.exists():
        logger.error("В распакованном архиве нет директории data/ — проверьте arcname.")
        return

    ok = compare_trees(DATA_DIR, restored_data, logger)
    logger.info("Результат проверки: %s", "УСПЕХ" if ok else "ЕСТЬ РАСХОЖДЕНИЯ")
    logger.info("=" * 60)


run()