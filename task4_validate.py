"""
Задание 4 (часть 2): JSON Schema + валидация processed_files_info.json.
Печатает отчёт по каждой найденной ошибке (путь + сообщение).
"""
import json
import logging
from datetime import datetime

from config import LOG_FILE, OUTPUT_DIR

JSON_IN = OUTPUT_DIR / "processed_files_info.json"
SCHEMA_IN = OUTPUT_DIR / "processed_files_info.schema.json"

SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://example.local/processed_files_info.schema.json",
    "title": "ProcessedFilesInfo",
    "type": "object",
    "required": ["generated_at", "records_count", "files"],
    "additionalProperties": False,
    "properties": {
        "generated_at": {"type": "string", "format": "date-time"},
        "records_count": {"type": "integer", "minimum": 0},
        "files": {
            "type": "array",
            "items": {"$ref": "#/$defs/file_info"},
        },
    },
    "$defs": {
        "file_info": {
            "type": "object",
            "required": [
                "file_name", "full_path", "size_bytes", "created_at", "modified_at"
            ],
            "additionalProperties": False,
            "properties": {
                "file_name": {"type": "string", "minLength": 1},
                "full_path": {"type": "string", "minLength": 1},
                "size_bytes": {"type": "integer", "minimum": 0},
                "created_at": {"type": "string", "format": "date-time"},
                "modified_at": {"type": "string", "format": "date-time"},
            },
        }
    },
}


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


def run() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 4 (часть 2): %s", datetime.now().isoformat(timespec="seconds"))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    SCHEMA_IN.write_text(
        json.dumps(SCHEMA, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    logger.info("Схема сохранена: %s", SCHEMA_IN)

    if not JSON_IN.exists():
        logger.error("Не найден %s — выполните task4_serialize.py.", JSON_IN)
        return

    try:
        import jsonschema
        from jsonschema import Draft202012Validator
    except ImportError:
        logger.error(
            "Не установлен пакет jsonschema. Установите: pip install jsonschema"
        )
        return

    try:
        instance = json.loads(JSON_IN.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        logger.error("JSON не парсится: %s (строка %d, колонка %d)", e.msg, e.lineno, e.colno)
        return

    try:
        Draft202012Validator.check_schema(SCHEMA)
        logger.info("Схема валидна.")
    except jsonschema.SchemaError as e:
        logger.error("Схема некорректна: %s", e.message)
        return

    validator = Draft202012Validator(SCHEMA, format_checker=Draft202012Validator.FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))

    if not errors:
        logger.info("Валидация пройдена: ошибок не найдено.")
        logger.info("Записей в files: %d (по данным records_count: %s)",
                    len(instance.get("files", [])), instance.get("records_count"))
        logger.info("=" * 60)
        return

    logger.error("Найдено ошибок валидации: %d", len(errors))
    for i, err in enumerate(errors, 1):
        path = "/".join(str(p) for p in err.absolute_path) or "<root>"
        logger.error("  [%d] %s: %s", i, path, err.message)
        if err.context:
            for suberr in err.context:
                sub_path = "/".join(str(p) for p in suberr.absolute_path) or "<root>"
                logger.error("      └ %s: %s", sub_path, suberr.message)

    logger.info("=" * 60)


run()