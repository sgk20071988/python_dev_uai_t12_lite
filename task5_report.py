"""
Задание 5: итоговый отчёт в output/report.md и output/report.pdf.

Содержит три раздела:
  1. Возникшие трудности и способы их решения
  2. Выводы
  3. Предложенные улучшения

Требуется: pip install reportlab (для PDF; для Markdown — не нужно).
"""
import logging
from datetime import datetime
from pathlib import Path

from config import LOG_FILE, OUTPUT_DIR
from report_model import Report, render_markdown

REPORT_MD_OUT  = OUTPUT_DIR / "report.md"
REPORT_PDF_OUT = OUTPUT_DIR / "report.pdf"


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


# ---------- Построение отчёта ----------
def build_report() -> Report:
    now = datetime.now().isoformat(timespec="seconds")
    rep = Report(
        title="Отчёт по домашнему заданию",
        subtitle=f"Файлы, пути, кодировки, сериализация — {now}",
    )

    # --- 1. Трудности ---
    rep.h1("1. Возникшие трудности и способы их решения")
    rep.bullets([
        "Автоопределение кодировки на коротких текстах: charset-normalizer иногда ошибается при <50 байт. "
        "Решение — fallback UTF-8 → ISO-8859-1 → cp1251 → Latin-1, плюс запись source_encoding в JSON.",
        "Инверсия регистра и Unicode: str.swapcase() для ß даёт SS (по стандарту Unicode), а не ẞ. "
        "Для задачи приемлемо, но важно осознавать: регистр в Unicode — не всегда «одна буква в одну».",
        "Сохранение структуры в zip: zipfile.write по умолчанию кладёт только имя файла. "
        "Решение — явный arcname=path.relative_to(DATA_DIR.parent).as_posix().",
        "Проверка целостности: распаковка поверх data/ сравнивает файл с самим собой. "
        "Решение — восстановление в data_restored/ и сравнение по SHA-256.",
        "JSON Schema и format: по умолчанию jsonschema не проверяет format: date-time, "
        "нужен явный format_checker. Без него валидация дат «молча» проходит.",
        "st_ctime на Linux — inode change time, а не creation time. В реальном проекте лучше "
        "st_birthtime (где доступно) или platform-specific логика.",
    ])

    # --- 2. Выводы ---
    rep.h1("2. Выводы")
    rep.bullets([
        "Сквозное логирование (logging) во всех модулях даёт воспроизводимость: "
        "по logs/project.log можно восстановить ход выполнения без перезапуска.",
        "Разделение «чтение/преобразование» и «сериализация» упрощает отладку: "
        "шаги можно перезапускать независимо.",
        "JSON Schema с additionalProperties: false — хороший контракт: "
        "при расширении FileInfo забыть обновить схему не получится.",
        "Единая точка запуска (run_all.py) с subprocess и perf_counter изолирует падения "
        "и упрощает проверку всего пайплайна одной командой.",
    ])

    # --- 3. Улучшения ---
    rep.h1("3. Предложенные улучшения")
    rep.bullets([
        "Вынести setup_logging в logging_config.py — сейчас он дублируется в каждом модуле.",
        "Хранить в FileInfo относительный путь (относительно PROJECT_ROOT) вместо абсолютного — "
        "артефакт не будет привязан к машине.",
        "Добавить проверку согласованности records_count и len(files) (инвариант приложения, "
        "не JSON Schema) — кастомная проверка после валидации.",
        "Git LFS для backups/ — zip-архивы быстро растят репозиторий."
    ])

    return rep


# ---------- PDF-рендерер ----------
def render_pdf(report: Report, out_path: Path, logger: logging.Logger) -> bool:
    """
    Рендерит Report в PDF через reportlab.
    Возвращает True при успехе, False если reportlab/шрифт недоступны.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle,
        )
    except ImportError:
        logger.error("reportlab не установлен. pip install reportlab")
        return False

    # --- Шрифт с кириллицей ---
    font_name = "Helvetica"  # запасной вариант (без кириллицы!)
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            try:
                pdfmetrics.registerFont(TTFont("ReportFont", path))
                bold_path = path.replace("Sans.ttf", "Sans-Bold.ttf").replace("arial.ttf", "arialbd.ttf")
                if Path(bold_path).exists():
                    pdfmetrics.registerFont(TTFont("ReportFont-Bold", bold_path))
                else:
                    pdfmetrics.registerFontFamily(
                        "ReportFont",
                        normal="ReportFont", bold="ReportFont",
                        italic="ReportFont", boldItalic="ReportFont",
                    )
                font_name = "ReportFont"
                logger.info("PDF: используется шрифт %s", path)
                break
            except Exception as e:
                logger.warning("Не удалось загрузить шрифт %s: %s", path, e)

    if font_name == "Helvetica":
        logger.warning(
            "PDF: не найден TTF с кириллицей — кириллица может отобразиться как '?'"
        )

    # --- Стили ---
    styles = {
        "title":   ParagraphStyle("Title",   fontName=font_name, fontSize=18, leading=22, spaceAfter=6),
        "subtitle":ParagraphStyle("Sub",     fontName=font_name, fontSize=10, leading=14,
                                  textColor=colors.grey, spaceAfter=14),
        "h1":      ParagraphStyle("H1",      fontName=font_name, fontSize=14, leading=18,
                                  spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1f3a5f")),
        "body":    ParagraphStyle("Body",    fontName=font_name, fontSize=10, leading=14, spaceAfter=6),
        "code":    ParagraphStyle("Code",    fontName=font_name, fontSize=8.5, leading=11,
                                  leftIndent=6, backColor=colors.HexColor("#f3f3f3"),
                                  borderPadding=4, spaceAfter=8),
        "bullet":  ParagraphStyle("Bullet",  fontName=font_name, fontSize=10, leading=14,
                                  leftIndent=14, bulletIndent=4, spaceAfter=3),
        "cell":    ParagraphStyle("Cell",    fontName=font_name, fontSize=9, leading=12),
        "cellh":   ParagraphStyle("CellH",   fontName=font_name, fontSize=9, leading=12,
                                  textColor=colors.white),
    }

    # --- Сборка story ---
    story = [
        Paragraph(report.title, styles["title"]),
        Paragraph(report.subtitle, styles["subtitle"]),
    ]

    for b in report.blocks:
        if b.kind == "h1":
            story.append(Paragraph(b.payload, styles["h1"]))
        elif b.kind == "h2":
            story.append(Paragraph(b.payload, styles["h1"]))
        elif b.kind == "p":
            story.append(Paragraph(b.payload, styles["body"]))
        elif b.kind == "code":
            story.append(Preformatted(b.payload, styles["code"]))
        elif b.kind == "bullets":
            for item in b.payload:
                story.append(Paragraph(item, styles["bullet"], bulletText="•"))
        elif b.kind == "table":
            headers = [Paragraph(h, styles["cellh"]) for h in b.payload["headers"]]
            data = [headers] + [
                [Paragraph(str(c), styles["cell"]) for c in row]
                for row in b.payload["rows"]
            ]
            tbl = Table(data, repeatRows=1, hAlign="LEFT", colWidths=None)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 4 * mm))

    # --- Документ ---
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=report.title,
        author="HW project",
    )
    try:
        doc.build(story)
        logger.info("PDF записан: %s (%d байт)", out_path, out_path.stat().st_size)
        return True
    except Exception as e:
        logger.exception("Ошибка при сборке PDF: %s", e)
        return False


def main() -> None:
    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Запуск Задания 5 (отчёт): %s", datetime.now().isoformat(timespec="seconds"))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()

    # Markdown — всегда
    md = render_markdown(report)
    REPORT_MD_OUT.write_text(md, encoding="utf-8")
    logger.info("Markdown записан: %s (%d байт)", REPORT_MD_OUT, REPORT_MD_OUT.stat().st_size)

    # PDF — если получится
    render_pdf(report, REPORT_PDF_OUT, logger)

    logger.info("=" * 60)


if __name__ == "__main__":
    main()