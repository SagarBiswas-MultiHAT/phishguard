"""SQLite storage backend with transactional safety."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from .model import Task
from .storage import Storage


class SQLiteStorage(Storage):
    """Persist tasks in a local SQLite database."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"
            )
            row = conn.execute("SELECT version FROM schema_version").fetchone()
            if row is None:
                conn.execute("INSERT INTO schema_version (version) VALUES (1)")
                self._migrate_v1(conn)

    def _migrate_v1(self, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

    def load_tasks(self) -> List[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT task_id, title, created_at FROM tasks ORDER BY rowid ASC"
            ).fetchall()
        return [
            Task(title=title, created_at=_parse_dt(created_at), task_id=task_id)
            for task_id, title, created_at in rows
        ]

    def save_tasks(self, tasks: Iterable[Task]) -> None:
        with self._connect() as conn:
            conn.execute("BEGIN")
            conn.execute("DELETE FROM tasks")
            conn.executemany(
                "INSERT INTO tasks (task_id, title, created_at) VALUES (?, ?, ?)",
                [
                    (task.task_id, task.title, task.created_at.isoformat())
                    for task in tasks
                ],
            )
            conn.commit()


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)
