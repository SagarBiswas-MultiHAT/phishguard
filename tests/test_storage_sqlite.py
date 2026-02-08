from __future__ import annotations

from pathlib import Path

from todo_app.model import Task
from todo_app.storage_sqlite import SQLiteStorage


def _make_tasks(count: int) -> list[Task]:
    return [Task(title=f"Task {index}") for index in range(count)]


def test_sqlite_roundtrip(tmp_path: Path) -> None:
    storage = SQLiteStorage(tmp_path / "tasks.db")
    tasks = [Task(title="Alpha"), Task(title="Beta")]
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert [task.title for task in loaded] == ["Alpha", "Beta"]


def test_sqlite_save_empty_resets(tmp_path: Path) -> None:
    storage = SQLiteStorage(tmp_path / "tasks.db")
    storage.save_tasks([Task(title="Alpha")])
    storage.save_tasks([])
    assert storage.load_tasks() == []


def test_sqlite_unicode_and_large_list(tmp_path: Path) -> None:
    storage = SQLiteStorage(tmp_path / "tasks.db")
    tasks = _make_tasks(300)
    tasks.append(Task(title="Cafe - unicode \u2603"))
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert loaded[-1].title == "Cafe - unicode \u2603"
    assert len(loaded) == 301
