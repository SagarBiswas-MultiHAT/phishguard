"""Controller bridging the view and model."""

from __future__ import annotations

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .model import Task, TaskList
from .storage import Storage

logger = logging.getLogger(__name__)


class Controller:
    """Orchestrates storage and model operations."""

    def __init__(self, storage: Storage) -> None:
        self.storage = storage
        self.model = TaskList()

    def load(self) -> List[Task]:
        try:
            tasks = self.storage.load_tasks()
            self.model.replace_all(tasks)
            return self.model.list()
        except Exception:
            logger.exception("Failed to load tasks")
            raise

    def save(self) -> None:
        try:
            self.storage.save_tasks(self.model.list())
        except Exception:
            logger.exception("Failed to save tasks")
            raise

    def add_task(self, title: str) -> Task:
        task = self.model.add(title)
        self.save()
        return task

    def remove_task(self, task_id: str) -> Task:
        task = self.model.remove_by_id(task_id)
        self.save()
        return task

    def undo_remove(self) -> Task | None:
        task = self.model.undo_last_removal()
        if task is not None:
            self.save()
        return task

    def search(self, query: str) -> List[Task]:
        return self.model.search(query)

    def export_json(self, path: Path) -> None:
        data = [_task_to_dict(task) for task in self.model.list()]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def import_json(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        tasks = [_task_from_mapping(item) for item in data]
        self.model.replace_all(tasks)
        self.save()

    def export_csv(self, path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["task_id", "title", "created_at"])
            for task in self.model.list():
                writer.writerow([task.task_id, task.title, task.created_at.isoformat()])

    def import_csv(self, path: Path) -> None:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            tasks = [_task_from_mapping(row) for row in reader]
        self.model.replace_all(tasks)
        self.save()


def _task_to_dict(task: Task) -> dict[str, str]:
    return {
        "task_id": task.task_id,
        "title": task.title,
        "created_at": task.created_at.isoformat(),
    }


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _task_from_mapping(data: dict[str, str]) -> Task:
    missing = {"task_id", "title", "created_at"} - set(data.keys())
    if missing:
        raise ValueError(f"Missing task fields: {', '.join(sorted(missing))}")
    return Task(
        title=data["title"],
        created_at=_parse_dt(data["created_at"]),
        task_id=data["task_id"],
    )
