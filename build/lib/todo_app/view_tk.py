"""Tkinter view for the To-Do List app."""

from __future__ import annotations

import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from .controller import Controller

logger = logging.getLogger(__name__)


class TkView:
    """Tkinter view bound to a controller."""

    def __init__(self, root: tk.Tk, controller: Controller) -> None:
        self.root = root
        self.controller = controller
        self.displayed_task_ids: list[str] = []

        self.root.title("To-Do List App")
        self.root.geometry("420x480")
        self._center_window(420, 480)

        self._build_menu()
        self._build_widgets()
        self._bind_shortcuts()

        self.refresh()

    def _build_menu(self) -> None:
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Import JSON", command=self.import_json)
        file_menu.add_command(label="Export JSON", command=self.export_json)
        file_menu.add_command(label="Import CSV", command=self.import_csv)
        file_menu.add_command(label="Export CSV", command=self.export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

    def _build_widgets(self) -> None:
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.task_entry = tk.Entry(frame, width=40)
        self.task_entry.pack(pady=(0, 6), fill=tk.X)

        self.add_button = tk.Button(frame, text="Add Task", command=self.add_task)
        self.add_button.pack(pady=(0, 10))

        search_frame = tk.Frame(frame)
        search_frame.pack(fill=tk.X)
        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        self.search_entry.bind("<KeyRelease>", lambda _event: self.refresh())

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

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda _event: self.add_task())
        self.root.bind("<Delete>", lambda _event: self.remove_task())
        self.root.bind("<Control-f>", lambda _event: self.focus_search())

        # center the starting window 

    def _center_window(self, width: int, height: int) -> None:
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def focus_search(self) -> None:
        self.search_entry.focus_set()

    def refresh(self) -> None:
        query = self.search_entry.get()
        tasks = self.controller.search(query)
        self.displayed_task_ids = [task.task_id for task in tasks]
        self.task_listbox.delete(0, tk.END)
        for task in tasks:
            self.task_listbox.insert(tk.END, task.display())

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
