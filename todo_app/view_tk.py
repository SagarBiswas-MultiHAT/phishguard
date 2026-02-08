"""Tkinter view for the To-Do List app."""

from __future__ import annotations

import contextlib
import ctypes
import logging
import sys
import tkinter as tk
from ctypes import wintypes
from pathlib import Path
from tkinter import filedialog, messagebox

from .controller import Controller
from .paths import get_user_data_dir

logger = logging.getLogger(__name__)


class TkView:
    """Tkinter view bound to a controller."""

    def __init__(
        self,
        root: tk.Tk | tk.Toplevel,
        controller: Controller,
        *,
        private_mode: bool = False,
    ) -> None:
        self.root = root
        self.controller = controller
        self.displayed_task_ids: list[str] = []
        self.private_mode = private_mode
        self._centered_on_map = False
        self._search_job: str | None = None
        self._last_query = ""

        self.root.title("To-Do List App")
        self.root.minsize(420, 480)

        self._build_menu()
        self._build_widgets()
        self._bind_shortcuts()
        self.root.bind("<Map>", self._on_map_center)

        self.refresh()
        self._set_window_size(420, 480)

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(
            label="Import JSON",
            command=self.import_json,
            accelerator="Ctrl+I",
        )
        file_menu.add_command(
            label="Export JSON",
            command=self.export_json,
            accelerator="Ctrl+E",
        )
        file_menu.add_command(
            label="Import CSV",
            command=self.import_csv,
            accelerator="Ctrl+Shift+I",
        )
        file_menu.add_command(
            label="Export CSV",
            command=self.export_csv,
            accelerator="Ctrl+Shift+E",
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="File", menu=file_menu)

        io_menu = tk.Menu(menu, tearoff=0)
        io_menu.add_command(
            label="Import JSON",
            command=self.import_json,
            accelerator="Ctrl+I",
        )
        io_menu.add_command(
            label="Export JSON",
            command=self.export_json,
            accelerator="Ctrl+E",
        )
        io_menu.add_command(
            label="Import CSV",
            command=self.import_csv,
            accelerator="Ctrl+Shift+I",
        )
        io_menu.add_command(
            label="Export CSV",
            command=self.export_csv,
            accelerator="Ctrl+Shift+E",
        )
        menu.add_cascade(label="Import/Export", menu=io_menu)

        if not self.private_mode:
            private_menu = tk.Menu(menu, tearoff=0)
            private_menu.add_command(
                label="Open Private Tasks",
                command=lambda: self._open_private_tasks(focus_entry=False),
            )
            private_menu.add_command(
                label="New Private Task",
                command=lambda: self._open_private_tasks(focus_entry=True),
            )
            menu.add_cascade(label="Private Tasks", menu=private_menu)
        self.root.config(menu=menu)

    def _build_widgets(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.task_entry = tk.Entry(frame, width=40)
        self.task_entry.pack(pady=(0, 6), fill=tk.X)
        self.task_entry.bind("<Return>", lambda _event: self.add_task())

        self.add_button = tk.Button(frame, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=(0, 10))

        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        self.search_entry.bind("<KeyRelease>", lambda _event: self._schedule_refresh())

        self.task_listbox = tk.Listbox(frame, width=40, height=12)
        self.task_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X)
        self.remove_button = tk.Button(
            button_frame, text="Remove Task", command=self.remove_task
        )
        self.remove_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
        self.undo_button = tk.Button(
            button_frame, text="Undo Remove", command=self.undo_remove
        )
        self.undo_button.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        status.pack(fill=tk.X, padx=12, pady=(0, 8))

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda _event: self.add_task())
        self.root.bind("<Delete>", lambda _event: self.remove_task())
        self.root.bind("<Control-f>", lambda _event: self.focus_search())
        self.root.bind("<Control-i>", lambda _event: self.import_json())
        self.root.bind("<Control-e>", lambda _event: self.export_json())
        self.root.bind("<Control-I>", lambda _event: self.import_csv())
        self.root.bind("<Control-E>", lambda _event: self.export_csv())

    def _set_window_size(self, width: int, height: int) -> None:
        self.root.withdraw()
        self.root.geometry(f"{width}x{height}")
        self.root.update_idletasks()
        self._center_window()
        self.root.deiconify()
        self.root.after(100, self._center_window)

    def _on_map_center(self, _event: tk.Event) -> None:
        if self._centered_on_map:
            return
        self._centered_on_map = True
        self.root.after(50, self._center_window)

    def _center_child_window(self, child: tk.Toplevel, width: int, height: int) -> None:
        self.root.update_idletasks()
        child.update_idletasks()
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_w = self.root.winfo_width() or self.root.winfo_reqwidth()
        parent_h = self.root.winfo_height() or self.root.winfo_reqheight()
        x = parent_x + max(0, (parent_w - width) // 2)
        y = parent_y + max(0, (parent_h - height) // 2)
        child.geometry(f"{width}x{height}+{x}+{y}")

    def _center_window(self) -> None:
        self.root.update_idletasks()
        if self._center_windows():
            return

        if isinstance(self.root, tk.Tk):
            try:
                self.root.eval("tk::PlaceWindow . center")
                return
            except tk.TclError:
                pass

        width = self.root.winfo_width() or self.root.winfo_reqwidth()
        height = self.root.winfo_height() or self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max(0, (screen_width // 2) - (width // 2))
        y = max(0, (screen_height // 2) - (height // 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _center_windows(self) -> bool:
        if sys.platform != "win32":
            return False

        hwnd = self.root.winfo_id()
        if not hwnd:
            return False

        user32 = ctypes.windll.user32
        with contextlib.suppress(AttributeError):
            user32.SetProcessDPIAware()

        class MonitorInfo(ctypes.Structure):
            _fields_ = [
                ("cbSize", wintypes.DWORD),
                ("rcMonitor", wintypes.RECT),
                ("rcWork", wintypes.RECT),
                ("dwFlags", wintypes.DWORD),
            ]

        class Point(ctypes.Structure):
            _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return False
        outer_w = rect.right - rect.left
        outer_h = rect.bottom - rect.top
        if outer_w <= 0 or outer_h <= 0:
            return False

        point = Point()
        monitor = 0
        if user32.GetCursorPos(ctypes.byref(point)):
            monitor = user32.MonitorFromPoint(point, 2)
        if not monitor:
            monitor = user32.MonitorFromWindow(hwnd, 2)
        info = MonitorInfo(cbSize=ctypes.sizeof(MonitorInfo))
        if not user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
            return False

        monitor_rect = info.rcMonitor
        monitor_w = monitor_rect.right - monitor_rect.left
        monitor_h = monitor_rect.bottom - monitor_rect.top
        x = monitor_rect.left + max(0, (monitor_w - outer_w) // 2)
        y = monitor_rect.top + max(0, (monitor_h - outer_h) // 2)
        swp_nosize = 0x0001
        swp_nozorder = 0x0004
        swp_noactivate = 0x0010
        return bool(
            user32.SetWindowPos(
                hwnd, 0, x, y, 0, 0, swp_nosize | swp_nozorder | swp_noactivate
            )
        )

    def _prompt_password_dialog(self, title: str) -> str | None:
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        width = 360
        height = 150
        self._center_child_window(dialog, width, height)

        label = tk.Label(dialog, text="Enter storage password:")
        label.pack(pady=(12, 6))
        entry = tk.Entry(dialog, show="*")
        entry.pack(padx=16, fill=tk.X)
        entry.focus_set()

        result: dict[str, str | None] = {"value": None}

        def confirm() -> None:
            value = entry.get().strip()
            result["value"] = value if value else None
            dialog.destroy()

        def cancel() -> None:
            result["value"] = None
            dialog.destroy()

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=12)
        tk.Button(button_frame, text="OK", width=10, command=confirm).pack(
            side=tk.LEFT, padx=8
        )
        tk.Button(button_frame, text="Cancel", width=10, command=cancel).pack(
            side=tk.LEFT, padx=8
        )
        dialog.protocol("WM_DELETE_WINDOW", cancel)
        dialog.wait_window()
        return result["value"]

    def _open_private_tasks(self, *, focus_entry: bool) -> None:
        password = self._prompt_password_dialog("Encrypted Storage")
        if not password:
            return

        try:
            from .storage_encrypted import EncryptedFileStorage
        except Exception as exc:
            messagebox.showerror("Encrypted Storage", str(exc))
            return

        data_dir = get_user_data_dir()
        storage = EncryptedFileStorage(
            data_dir / "private_tasks.enc",
            password=password,
        )
        controller = Controller(storage)
        try:
            controller.load()
        except Exception as exc:
            messagebox.showerror("Encrypted Storage", str(exc))
            return

        private_root = tk.Toplevel(self.root)
        private_root.title("Private Tasks")
        view = TkView(private_root, controller, private_mode=True)
        if focus_entry:
            view.task_entry.focus_set()

    def focus_search(self) -> None:
        self.search_entry.focus_set()

    def refresh(self) -> None:
        query = self.search_var.get()
        if query == self._last_query and self.displayed_task_ids:
            return
        self._last_query = query
        tasks = self.controller.search(query)
        self.displayed_task_ids = [task.task_id for task in tasks]
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            self.task_listbox.insert(tk.END, task.display())
        total = len(tasks)
        label = "Private tasks" if self.private_mode else "Tasks"
        self.status_var.set(f"{label}: {total}")

    def _schedule_refresh(self) -> None:
        if self._search_job is not None:
            self.root.after_cancel(self._search_job)
        self._search_job = self.root.after(150, self._apply_search)

    def _apply_search(self) -> None:
        self._search_job = None
        self.refresh()

    def add_task(self) -> None:
        title = self.task_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a task.")
            return
        try:
            self.controller.add_task(title)
            self.task_entry.delete(0, tk.END)
            self.refresh()
        except Exception as exc:
            logger.exception("Add task failed")
            messagebox.showerror("Error", str(exc))

    def remove_task(self) -> None:
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to remove.")
            return
        index = selection[0]
        task_id = self.displayed_task_ids[index]
        try:
            self.controller.remove_task(task_id)
            self.refresh()
        except Exception as exc:
            logger.exception("Remove task failed")
            messagebox.showerror("Error", str(exc))

    def undo_remove(self) -> None:
        task = self.controller.undo_remove()
        if task is None:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        self.refresh()

    def export_json(self) -> None:
        path = self._prompt_save_path("json")
        if not path:
            return
        self.controller.export_json(path)
        messagebox.showinfo("Export", "Tasks exported to JSON.")

    def import_json(self) -> None:
        path = self._prompt_open_path("json")
        if not path:
            return
        self.controller.import_json(path)
        self.refresh()
        messagebox.showinfo("Import", "Tasks imported from JSON.")

    def export_csv(self) -> None:
        path = self._prompt_save_path("csv")
        if not path:
            return
        self.controller.export_csv(path)
        messagebox.showinfo("Export", "Tasks exported to CSV.")

    def import_csv(self) -> None:
        path = self._prompt_open_path("csv")
        if not path:
            return
        self.controller.import_csv(path)
        self.refresh()
        messagebox.showinfo("Import", "Tasks imported from CSV.")

    def _prompt_save_path(self, ext: str) -> Path | None:
        filetypes = [(ext.upper(), f"*.{ext}")]
        filename = filedialog.asksaveasfilename(
            defaultextension=f".{ext}", filetypes=filetypes
        )
        return Path(filename) if filename else None

    def _prompt_open_path(self, ext: str) -> Path | None:
        filetypes = [(ext.upper(), f"*.{ext}")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        return Path(filename) if filename else None
