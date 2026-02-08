"""Command line entrypoints for the To-Do List app."""

from __future__ import annotations

import argparse
import contextlib
import ctypes
import getpass
import logging
import sys
from pathlib import Path

from .controller import Controller
from .logging_config import setup_logging
from .paths import get_user_data_dir
from .storage import Storage
from .storage_fs import FileStorage
from .storage_sqlite import SQLiteStorage

logger = logging.getLogger(__name__)


def build_storage(args: argparse.Namespace) -> Storage:
    data_dir = Path(args.data_dir) if args.data_dir else get_user_data_dir()
    if args.storage == "sqlite":
        return SQLiteStorage(data_dir / "tasks.db")
    if args.storage == "encrypted":
        from .storage_encrypted import EncryptedFileStorage

        password = args.password or getpass.getpass("Storage password: ")
        return EncryptedFileStorage(data_dir / "tasks.enc", password=password)
    return FileStorage(data_dir / "tasks.txt")


def run_ui(args: argparse.Namespace) -> int:
    import tkinter as tk
    from tkinter import messagebox, simpledialog

    _set_windows_dpi_awareness()
    setup_logging()
    root = tk.Tk()
    root.withdraw()
    if args.storage == "encrypted" and not args.password:
        password = simpledialog.askstring(
            "Encrypted Storage",
            "Enter storage password:",
            show="*",
            parent=root,
        )
        if not password:
            messagebox.showinfo(
                "Encrypted Storage",
                "A password is required to open encrypted storage.",
                parent=root,
            )
            root.destroy()
            return 1
        args.password = password
    storage = build_storage(args)
    controller = Controller(storage)
    controller.load()
    from .view_tk import TkView

    root.deiconify()
    TkView(root, controller)
    root.mainloop()
    return 0


def _set_windows_dpi_awareness() -> None:
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        with contextlib.suppress(Exception):
            ctypes.windll.user32.SetProcessDPIAware()


def export_tasks(args: argparse.Namespace) -> int:
    setup_logging()
    storage = build_storage(args)
    controller = Controller(storage)
    controller.load()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "json":
        controller.export_json(output)
    else:
        controller.export_csv(output)
    return 0


def backup_tasks(args: argparse.Namespace) -> int:
    setup_logging()
    storage = build_storage(args)
    controller = Controller(storage)
    controller.load()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    controller.export_json(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="To-Do List App")
    parser.add_argument(
        "--storage",
        choices=["fs", "sqlite", "encrypted"],
        default="fs",
    )
    parser.add_argument("--data-dir", help="Override storage directory")
    parser.add_argument("--password", help="Password for encrypted storage")

    subparsers = parser.add_subparsers(dest="command")

    ui_parser = subparsers.add_parser("ui", help="Launch the Tkinter UI")
    ui_parser.set_defaults(func=run_ui)

    export_parser = subparsers.add_parser("export", help="Export tasks to JSON or CSV")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json")
    export_parser.add_argument("--output", required=True)
    export_parser.set_defaults(func=export_tasks)

    backup_parser = subparsers.add_parser("backup", help="Headless backup to JSON")
    backup_parser.add_argument("--output", required=True)
    backup_parser.set_defaults(func=backup_tasks)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        args.command = "ui"
        args.func = run_ui
    try:
        return args.func(args)
    except Exception as exc:
        logger.exception("Command failed")
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
