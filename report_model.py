"""
Модель отчёта: список блоков. Из неё рендерим и Markdown, и PDF.
Блоки:
  ("h1", text), ("h2", text), ("p", text), ("code", text),
  ("table", {"headers": [...], "rows": [[...], ...]}), ("bullets", [str, ...])
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReportBlock:
    kind: str
    payload: Any


@dataclass
class Report:
    title: str
    subtitle: str
    blocks: list[ReportBlock] = field(default_factory=list)

    def h1(self, text: str) -> Report:
        self.blocks.append(ReportBlock("h1", text)); return self

    def h2(self, text: str) -> Report:
        self.blocks.append(ReportBlock("h2", text)); return self

    def p(self, text: str) -> Report:
        self.blocks.append(ReportBlock("p", text)); return self

    def code(self, text: str) -> Report:
        self.blocks.append(ReportBlock("code", text)); return self

    def table(self, headers: list[str], rows: list[list[str]]) -> Report:
        self.blocks.append(ReportBlock("table", {"headers": headers, "rows": rows})); return self

    def bullets(self, items: list[str]) -> Report:
        self.blocks.append(ReportBlock("bullets", items)); return self


# ---------- Рендерер Markdown ----------
def render_markdown(report: Report) -> str:
    out: list[str] = [f"# {report.title}", "", f"*{report.subtitle}*", ""]
    for b in report.blocks:
        if b.kind == "h1":
            out += [f"## {b.payload}", ""]
        elif b.kind == "h2":
            out += [f"### {b.payload}", ""]
        elif b.kind == "p":
            out += [b.payload, ""]
        elif b.kind == "code":
            out += ["```", b.payload, "```", ""]
        elif b.kind == "bullets":
            out += [f"- {item}" for item in b.payload] + [""]
        elif b.kind == "table":
            headers = b.payload["headers"]
            rows = b.payload["rows"]
            out.append("| " + " | ".join(headers) + " |")
            out.append("|" + "|".join(["---"] * len(headers)) + "|")
            for r in rows:
                out.append("| " + " | ".join(str(c) for c in r) + " |")
            out.append("")
    return "\n".join(out)