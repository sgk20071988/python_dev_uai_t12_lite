"""
Задание 2 (часть 1): чтение data/raw/, определение кодировки,
инверсия регистра, запись в data/processed/ с суффиксом _processed.
"""
import logging
from datetime import datetime
from pathlib import Path

from config import RAW_DIR, PROCESSED_DIR, LOG_FILE

try:
    from charset_normalizer import from_bytes
    _HAS_CHARSET_NORMALIZER = True
except ImportError:
    _HAS_CHARSET_NORMALIZER = False


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


def detect_encoding(raw_bytes: bytes, logger: logging.Logger, fname: str) -> str:
    """
    Определяет кодировку байтов.
    Приоритет: charset-normalizer -> ручной fallback.
    """
    if _HAS_CHARSET_NORMALIZER:
        result = from_bytes(raw_bytes).best()
        if result is not None:
            enc = result.encoding
            logger.info("Кодировка %s определена для %s (charset-normalizer)", enc, fname)
            return enc
        logger.warning("charset-normalizer не смог определить кодировку для %s", fname)

    for enc in ("utf-8", "iso-8859-1"):
        try:
            raw_bytes.decode(enc)
            logger.info("Кодировка %s подобрана для %s (fallback)", enc, fname)
            return enc
        except UnicodeDecodeError:
            continue

    logger.warning("Не удалось определить кодировку для %s, используем iso-8859-1", fname)
    return "iso-8859-1"


def swap_case(text: str) -> str:
    """Меняет регистр всех букв: заглавные -> строчные, строчные -> заглавные."""
    return text.swapcase()


def process_file(path: Path, logger: logging.Logger) -> Path:
    """Читает файл, определяет кодировку, инвертирует регистр, пишет *_processed."""
    raw_bytes = path.read_bytes()
    encoding = detect_encoding(raw_bytes, logger, path.name)

    try:
        text = raw_bytes.decode(encoding)
    except UnicodeDecodeError:
        logger.warning("Не удалось декодировать %s как %s, используем iso-8859-1", path.name, encoding)
        encoding = "iso-8859-1"
        text = raw_bytes.decode(encoding)

    processed = swap_case(text)

    out_name = path.stem + "_processed" + path.suffix
    out_path = PROCESSED_DIR / out_name
    out_path.write_text(processed, encoding="utf-8")

    logger.info(
        "Обработан %s (enc=%s) -> %s (%d байт входа -> %d байт UTF-8 выхода)",
        path.name, encoding, out_name, len(raw_bytes), out_path.stat().st_size,
    )
    return out_path


def run() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 2 (часть 1): %s", datetime.now().isoformat(timespec="seconds"))

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.glob("*.txt"))
    if not files:
        logger.error("В %s нет .txt файлов. Сначала выполните Задание 1.", RAW_DIR)
        return

    for path in files:
        process_file(path, logger)

    logger.info("Задание 2 (часть 1) завершено. Обработано файлов: %d", len(files))
    logger.info("=" * 60)


run()