from __future__ import annotations

import pytest

from todo_app.model import TaskList


def test_add_and_list():
    tasks = TaskList()
    task = tasks.add("Buy milk")
    assert task.title == "Buy milk"
    assert tasks.tasks() == [task]


def test_add_rejects_empty():
    tasks = TaskList()
    with pytest.raises(ValueError):
        tasks.add("   ")


def test_remove_and_undo():
    tasks = TaskList()
    task = tasks.add("Task")
    tasks.remove_by_id(task.task_id)
    assert tasks.tasks() == []
    tasks.undo_last_removal()
    assert len(tasks.tasks()) == 1


def test_search_filters():
    tasks = TaskList()
    tasks.add("Alpha")
    tasks.add("Beta")
    results = tasks.search("alp")
    assert len(results) == 1
    assert results[0].title == "Alpha"


def test_undo_without_removal_returns_none():
    tasks = TaskList()
    assert tasks.undo_last_removal() is None


def test_replace_all_resets_last_removed():
    tasks = TaskList()
    task = tasks.add("One")
    tasks.remove_by_id(task.task_id)
    tasks.replace_all([])
    assert tasks.undo_last_removal() is None
