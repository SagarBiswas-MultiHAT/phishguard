"""Storage interfaces for task persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from .model import Task


class Storage(ABC):
    """Abstract storage interface."""

    @abstractmethod
    def load_tasks(self) -> List[Task]:
        raise NotImplementedError

    @abstractmethod
    def save_tasks(self, tasks: Iterable[Task]) -> None:
        raise NotImplementedError
