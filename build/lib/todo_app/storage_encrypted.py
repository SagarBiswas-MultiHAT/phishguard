"""Encrypted file storage backend using Fernet."""

from __future__ import annotations

import base64
import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any, Iterable, List, TYPE_CHECKING

from .model import Task
from .storage import Storage
from .storage_fs import BACKUP_COUNT, _parse_dt, _rotate_backups, _task_to_dict

if TYPE_CHECKING:
    from cryptography.fernet import Fernet as FernetType
else:
    FernetType = Any

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except Exception:  # pragma: no cover - optional dependency
    Fernet = None
    InvalidToken = Exception
    PBKDF2HMAC = None
    hashes = None

SALT_BYTES = 16
ITERATIONS = 390_000


class EncryptedFileStorage(Storage):
    """Encrypt tasks with a password-derived key."""

    def __init__(self, path: Path, password: str, iterations: int = ITERATIONS) -> None:
        if Fernet is None or PBKDF2HMAC is None:
            raise RuntimeError(
                "cryptography is required for encrypted storage. Install extras: pip install .[encrypt]"
            )
        if not password:
            raise ValueError("Password must be provided for encrypted storage.")
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.password = password
        self.iterations = iterations
        self._lock = threading.Lock()

    def load_tasks(self) -> List[Task]:
        with self._lock:
            if not self.path.exists():
                return []
            with self.path.open("rb") as handle:
                payload = json.loads(handle.read().decode("utf-8"))
            salt = base64.b64decode(payload["salt"])
            token = payload["token"].encode("utf-8")
            iterations = int(payload.get("iterations", self.iterations))
            fernet = _build_fernet(self.password, salt, iterations)
            try:
                decrypted = fernet.decrypt(token)
            except InvalidToken as exc:
                raise ValueError("Invalid password or corrupted file.") from exc
            lines = decrypted.decode("utf-8").splitlines()
            tasks: List[Task] = []
            for line in lines:
                if not line.strip():
                    continue
                data = json.loads(line)
                tasks.append(
                    Task(
                        title=data["title"],
                        created_at=_parse_dt(data["created_at"]),
                        task_id=data["task_id"],
                    )
                )
            return tasks

    def save_tasks(self, tasks: Iterable[Task]) -> None:
        with self._lock:
            _rotate_backups(self.path, backup_count=BACKUP_COUNT)
            salt = os.urandom(SALT_BYTES)
            fernet = _build_fernet(self.password, salt, self.iterations)
            plaintext = "\n".join(
                json.dumps(_task_to_dict(task), ensure_ascii=False) for task in tasks
            ).encode("utf-8")
            token = fernet.encrypt(plaintext)
            payload = {
                "salt": base64.b64encode(salt).decode("utf-8"),
                "token": token.decode("utf-8"),
                "iterations": self.iterations,
            }
            _atomic_write_bytes(self.path, json.dumps(payload).encode("utf-8"))


def _build_fernet(password: str, salt: bytes, iterations: int) -> FernetType:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
    return Fernet(key)


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    temp_dir = path.parent
    fd, temp_path_str = tempfile.mkstemp(prefix="tasks-", dir=temp_dir)
    temp_path = Path(temp_path_str)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
