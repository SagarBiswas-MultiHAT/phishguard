"""Domain model for tasks and task lists."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class Task:
    """Represents a single to-do task."""

    title: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    task_id: str = field(default_factory=lambda: uuid4().hex)

    def display(self) -> str:
        """Return the display string for UI elements."""
        return self.title


class TaskList:
    """In-memory task list with search and undo support."""

    def __init__(self, tasks: Iterable[Task] | None = None) -> None:
        self._tasks: list[Task] = list(tasks or [])
        self._last_removed: Task | None = None

    def add(self, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")
        task = Task(title=title)
        self._tasks.append(task)
        return task

    def remove_by_id(self, task_id: str) -> Task:
        for index, task in enumerate(self._tasks):
            if task.task_id == task_id:
                self._last_removed = task
                del self._tasks[index]
                return task
        raise KeyError(f"Task id {task_id} not found.")

    def undo_last_removal(self) -> Task | None:
        if self._last_removed is None:
            return None
        task = self._last_removed
        self._tasks.append(task)
        self._last_removed = None
        return task

    def tasks(self) -> list[Task]:
        return list(self._tasks)

    def search(self, query: str) -> list[Task]:
        query = query.strip().lower()
        if not query:
            return self.tasks()
        return [task for task in self._tasks if query in task.title.lower()]

    def replace_all(self, tasks: Iterable[Task]) -> None:
        self._tasks = list(tasks)
        self._last_removed = None
