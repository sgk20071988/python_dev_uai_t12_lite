"""
Задание 2 (часть 2): сериализация содержимого data/processed/ и соответствующих
исходников из data/raw/ в output/processed_data.json.
"""
import json
import logging
from datetime import datetime
from pathlib import Path

from config import LOG_FILE, OUTPUT_DIR, PROCESSED_DIR, RAW_DIR

JSON_OUT = OUTPUT_DIR / "processed_data.json"


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


def read_text_safely(path: Path) -> str:
    """
    Читает текст, пытаясь декодировать в UTF-8. Если не выходит —
    использует charset-normalizer/fallback (на случай нестандартных файлов).
    """
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        from task2 import detect_encoding  # переиспользуем логику
        enc = detect_encoding(data, logging.getLogger("project"), path.name)
        return data.decode(enc, errors="replace")


def collect_records(logger: logging.Logger) -> list[dict]:
    """Собирает список записей: по одной на каждый *_processed.txt в data/processed/."""
    records: list[dict] = []

    for proc_path in sorted(PROCESSED_DIR.glob("*_processed.txt")):
        stem = proc_path.stem
        original_stem = stem.removesuffix("_processed")
        raw_path = RAW_DIR / (original_stem + proc_path.suffix)

        if not raw_path.exists():
            logger.warning("Не найден исходный файл %s для %s, пропускаем", raw_path.name, proc_path.name)
            continue

        from task2 import detect_encoding
        raw_bytes = raw_path.read_bytes()
        raw_enc = detect_encoding(raw_bytes, logger, raw_path.name)
        source_text = raw_bytes.decode(raw_enc, errors="replace")

        processed_text = read_text_safely(proc_path)

        record = {
            "file_name": raw_path.name,
            "source_encoding": raw_enc,
            "original_text": source_text,
            "processed_text": processed_text,
            "size_bytes": raw_path.stat().st_size,
            "last_modified": datetime.fromtimestamp(
                raw_path.stat().st_mtime
            ).isoformat(timespec="seconds"),
        }
        records.append(record)
        logger.info("Запись добавлена: %s", raw_path.name)

    return records


def run() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 2 (часть 2): %s", datetime.now().isoformat(timespec="seconds"))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = collect_records(logger)
    if not records:
        logger.error("Нет данных для сериализации. Выполните task2.py.")
        return

    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "records_count": len(records),
        "records": records,
    }

    JSON_OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "JSON записан: %s (%d записей, %d байт)",
        JSON_OUT, len(records), JSON_OUT.stat().st_size,
    )
    logger.info("=" * 60)


run()