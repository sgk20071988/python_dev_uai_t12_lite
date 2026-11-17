"""
Задание 1: Управление проектной структурой и файловой системой.
- Создание дерева директорий (идемпотентно).
- Создание текстовых файлов в разных кодировках.
- Логирование каждого шага в logs/project.log.
"""
import logging
from datetime import datetime
from pathlib import Path

from config import BACKUPS_DIR, LOG_FILE, LOGS_DIR, OUTPUT_DIR, PROCESSED_DIR, RAW_DIR


def setup_logging() -> logging.Logger:
    """Настраивает логгер: пишет в файл и в консоль."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("project")
    logger.setLevel(logging.INFO)

    # Чтобы повторный вызов setup_logging не дублировал хэндлеры
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    return logger


def create_directories(logger: logging.Logger) -> None:
    """Создаёт дерево директорий, если их ещё нет."""
    dirs = [
        RAW_DIR,
        PROCESSED_DIR,
        LOGS_DIR,
        BACKUPS_DIR,
        OUTPUT_DIR,
    ]
    for d in dirs:
        existed = d.exists()
        d.mkdir(parents=True, exist_ok=True)
        status = "уже существует" if existed else "создана"
        logger.info("Директория %s %s", d, status)


FILES_TO_CREATE = [
    # (имя файла, текст, кодировка)
    (
        "greeting_ru.txt",
        "Привет, мир! Это тестовый файл на русском языке.\n"
        "Здесь есть Заглавные и строчные Буквы.\n",
        "utf-8",
    ),
    (
        "greeting_en.txt",
        "Hello, World! This is a test file in English.\n"
        "It Has Mixed CASE Letters for the Case-Swap task.\n",
        "utf-8",
    ),
    (
        "greeting_de.txt",
        "Grüß Gott! Dies ist eine Testdatei auf Deutsch.\n"
        "Sie enthält Groß- und Kleinbuchstaben sowie Umlaute: ä ö ü ß.\n",
        "iso-8859-1",   # latin-1 — корректно кодирует немецкие умлауты
    ),
    (
        "greeting_fr.txt",
        "Bonjour le monde! Ceci est un fichier de test en français.\n"
        "Il contient des Lettres MAJUSCULES et minuscules, ainsi que des accents: é è à ç.\n",
        "iso-8859-1",
    ),
]


def create_raw_files(logger: logging.Logger) -> None:
    """Создаёт файлы в data/raw/ в разных кодировках."""
    for name, text, encoding in FILES_TO_CREATE:
        path = RAW_DIR / name
        path.write_text(text, encoding=encoding)
        size = path.stat().st_size
        logger.info(
            "Создан файл %s (кодировка=%s, размер=%d байт)",
            path.relative_to(RAW_DIR.parent.parent), encoding, size,
        )


def run() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 1: %s", datetime.now().isoformat(timespec="seconds"))

    create_directories(logger)
    create_raw_files(logger)

    logger.info("Задание 1 успешно завершено.")
    logger.info("=" * 60)

run()