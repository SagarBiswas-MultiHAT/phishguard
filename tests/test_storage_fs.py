from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from todo_app.model import Task
from todo_app.storage_fs import FileStorage


def _make_tasks(count: int) -> list[Task]:
    return [Task(title=f"Task {index}") for index in range(count)]


def test_fs_load_missing_returns_empty(tmp_path: Path) -> None:
    storage = FileStorage(tmp_path / "tasks.txt")
    assert storage.load_tasks() == []


def test_fs_save_and_load_roundtrip(tmp_path: Path) -> None:
    storage = FileStorage(tmp_path / "tasks.txt")
    tasks = [Task(title="Alpha"), Task(title="Beta")]
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert [task.title for task in loaded] == ["Alpha", "Beta"]


def test_fs_backup_rotation(tmp_path: Path) -> None:
    path = tmp_path / "tasks.txt"
    storage = FileStorage(path)
    storage.save_tasks([Task(title="First")])
    storage.save_tasks([Task(title="Second")])

    backup = path.with_suffix(path.suffix + ".bak1")
    assert backup.exists()
    backup_storage = FileStorage(backup)
    loaded = backup_storage.load_tasks()
    assert [task.title for task in loaded] == ["First"]


def test_fs_concurrent_save_is_atomic(tmp_path: Path) -> None:
    storage = FileStorage(tmp_path / "tasks.txt")
    tasks_a = _make_tasks(50)
    tasks_b = _make_tasks(120)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(storage.save_tasks, tasks_a),
            executor.submit(storage.save_tasks, tasks_b),
        ]
        for future in futures:
            future.result()

    loaded = storage.load_tasks()
    assert len(loaded) in {50, 120}


def test_fs_unicode_and_large_list(tmp_path: Path) -> None:
    storage = FileStorage(tmp_path / "tasks.txt")
    tasks = [Task(title="Mango")]
    tasks.extend(_make_tasks(500))
    tasks.append(Task(title="Cafe - unicode \u2603"))
    storage.save_tasks(tasks)
    loaded = storage.load_tasks()
    assert loaded[0].title == "Mango"
    assert loaded[-1].title == "Cafe - unicode \u2603"
