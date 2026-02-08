"""Top-level package for the To-Do List application."""

from .cli import main
from .model import Task, TaskList

__all__ = ["Task", "TaskList", "main"]

__version__ = "1.0.0"
