"""
Класс FileInfo: хранит информацию о файле и умеет (де)сериализоваться в/из dict.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class FileInfo:
    file_name: str
    full_path: str
    size_bytes: int
    created_at: str
    modified_at: str

    @classmethod
    def from_path(cls, path: Path) -> FileInfo:
        stat = path.stat()
        return cls(
            file_name=path.name,
            full_path=str(path.resolve()),
            size_bytes=stat.st_size,
            # st_ctime на Linux — inode change time; на Windows — creation time.
            # Для учебной задачи этого достаточно; уточнение — в комментарии.
            created_at=datetime.fromtimestamp(stat.st_ctime).isoformat(timespec="seconds"),
            modified_at=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FileInfo:
        required = {"file_name", "full_path", "size_bytes", "created_at", "modified_at"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"В словаре отсутствуют поля: {sorted(missing)}")

        if not isinstance(data["size_bytes"], int):
            raise TypeError(f"size_bytes должен быть int, получено {type(data['size_bytes']).__name__}")
        for key in ("created_at", "modified_at"):
            try:
                datetime.fromisoformat(data[key])
            except ValueError as e:
                raise ValueError(f"Поле {key} не является ISO-8601: {data[key]!r}") from e

        return cls(**{k: data[k] for k in required})

    def __str__(self) -> str:
        return (
            f"FileInfo({self.file_name}, size={self.size_bytes} B, "
            f"modified={self.modified_at})"
        )