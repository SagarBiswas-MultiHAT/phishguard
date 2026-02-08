"""Storage interfaces for task persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from .model import Task


class Storage(ABC):
    """Abstract storage interface."""

    @abstractmethod
    def load_tasks(self) -> list[Task]:
        raise NotImplementedError

    @abstractmethod
    def save_tasks(self, tasks: Iterable[Task]) -> None:
        raise NotImplementedError
