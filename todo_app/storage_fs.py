"""Filesystem storage backend with atomic writes and backups."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import threading
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from .model import Task
from .storage import Storage

BACKUP_COUNT = 5


class FileStorage(Storage):
    """Store tasks as line-delimited JSON text."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def load_tasks(self) -> list[Task]:
        with self._lock:
            if not self.path.exists():
                return []
            tasks: list[Task] = []
            with self.path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    tasks.append(
                        Task(
                            title=data["title"],
                            created_at=_parse_dt(data["created_at"]),
                            task_id=data["task_id"],
                        )
                    )
            return tasks

    def save_tasks(self, tasks: Iterable[Task]) -> None:
        with self._lock:
            _rotate_backups(self.path, BACKUP_COUNT)
            lines = [
                json.dumps(_task_to_dict(task), ensure_ascii=False) for task in tasks
            ]
            data = "\n".join(lines) + ("\n" if lines else "")
            _atomic_write_text(self.path, data)

    def _rotate_backups(self) -> None:
        _rotate_backups(self.path, BACKUP_COUNT)


def _task_to_dict(task: Task) -> dict[str, str]:
    return {
        "task_id": task.task_id,
        "title": task.title,
        "created_at": task.created_at.isoformat(),
    }


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _atomic_write_text(path: Path, data: str) -> None:
    temp_dir = path.parent
    fd, temp_path_str = tempfile.mkstemp(prefix="tasks-", dir=temp_dir)
    temp_path = Path(temp_path_str)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)


def _rotate_backups(path: Path, backup_count: int) -> None:
    if backup_count <= 0 or not path.exists():
        return
    for index in range(backup_count - 1, 0, -1):
        older = path.with_suffix(path.suffix + f".bak{index}")
        newer = path.with_suffix(path.suffix + f".bak{index + 1}")
        if older.exists():
            shutil.move(older, newer)
    first_backup = path.with_suffix(path.suffix + ".bak1")
    shutil.copy2(path, first_backup)
