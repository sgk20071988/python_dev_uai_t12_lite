"""
Задание 4 (часть 1): собрать FileInfo по всем файлам data/processed/ и сохранить в JSON.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from config import LOG_FILE, OUTPUT_DIR, PROCESSED_DIR
from file_info import FileInfo

JSON_OUT = OUTPUT_DIR / "processed_files_info.json"


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


def collect_infos(directory: Path, logger: logging.Logger) -> list[FileInfo]:
    files = sorted(p for p in directory.rglob("*") if p.is_file())
    if not files:
        logger.warning("В %s нет файлов.", directory)
    return [FileInfo.from_path(p) for p in files]


def run() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 4 (часть 1): %s", datetime.now().isoformat(timespec="seconds"))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    infos = collect_infos(PROCESSED_DIR, logger)
    if not infos:
        logger.error("Нечего сериализовать — выполните Задание 2.")
        return

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "records_count": len(infos),
        "files": [fi.to_dict() for fi in infos],
    }

    JSON_OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("JSON записан: %s (%d записей, %d байт)", JSON_OUT, len(infos), JSON_OUT.stat().st_size)

    reloaded = json.loads(JSON_OUT.read_text(encoding="utf-8"))
    restored = [FileInfo.from_dict(r) for r in reloaded["files"]]
    assert all(isinstance(fi, FileInfo) for fi in restored)
    logger.info("Десериализация проверена: восстановлено %d объектов FileInfo.", len(restored))
    for fi in restored:
        logger.info("  %s", fi)

    logger.info("=" * 60)


run()