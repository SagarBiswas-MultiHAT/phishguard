"""Path helpers for user data and configuration directories."""

from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "todo-app"


def _env_path(var_name: str) -> Path | None:
    value = os.environ.get(var_name)
    if not value:
        return None
    return Path(value)


def get_user_data_dir() -> Path:
    """Return the user-specific data directory."""
    if os.name == "nt":
        base = _env_path("APPDATA") or Path.home() / "AppData" / "Roaming"
        return base / APP_NAME
    if os.name == "posix":
        xdg = _env_path("XDG_DATA_HOME") or Path.home() / ".local" / "share"
        return xdg / APP_NAME
    return Path.home() / f".{APP_NAME}"


def get_user_config_dir() -> Path:
    """Return the user-specific config directory."""
    if os.name == "nt":
        base = _env_path("APPDATA") or Path.home() / "AppData" / "Roaming"
        return base / APP_NAME
    if os.name == "posix":
        xdg = _env_path("XDG_CONFIG_HOME") or Path.home() / ".config"
        return xdg / APP_NAME
    return Path.home() / f".{APP_NAME}"
