"""Encrypted file storage backend using Fernet."""

from __future__ import annotations

import base64
import json
import os
import tempfile
import threading
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .model import Task
from .storage import Storage
from .storage_fs import BACKUP_COUNT, _parse_dt, _rotate_backups, _task_to_dict

if TYPE_CHECKING:
    from cryptography.fernet import Fernet as FernetType
    from cryptography.fernet import InvalidToken as InvalidTokenType
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as PBKDF2HMACType
else:
    FernetType = Any
    InvalidTokenType = Exception
    PBKDF2HMACType = Any

SALT_BYTES = 16
ITERATIONS = 390_000


class EncryptedFileStorage(Storage):
    """Encrypt tasks with a password-derived key."""

    def __init__(self, path: Path, password: str, iterations: int = ITERATIONS) -> None:
        (
            self._fernet_cls,
            self._invalid_token,
            self._hashes_module,
            self._pbkdf2_cls,
        ) = _import_crypto_components()
        if not password:
            raise ValueError("Password must be provided for encrypted storage.")
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.password = password
        self.iterations = iterations
        self._lock = threading.Lock()

    def load_tasks(self) -> list[Task]:
        with self._lock:
            if not self.path.exists():
                return []
            with self.path.open("rb") as handle:
                payload = json.loads(handle.read().decode("utf-8"))
            salt = base64.b64decode(payload["salt"])
            token = payload["token"].encode("utf-8")
            iterations = int(payload.get("iterations", self.iterations))
            fernet = _build_fernet(
                password=self.password,
                salt=salt,
                iterations=iterations,
                fernet_cls=self._fernet_cls,
                hashes_module=self._hashes_module,
                pbkdf2_cls=self._pbkdf2_cls,
            )
            try:
                decrypted = fernet.decrypt(token)
            except self._invalid_token as exc:
                raise ValueError("Invalid password or corrupted file.") from exc
            lines = decrypted.decode("utf-8").splitlines()
            tasks: list[Task] = []
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
            fernet = _build_fernet(
                password=self.password,
                salt=salt,
                iterations=self.iterations,
                fernet_cls=self._fernet_cls,
                hashes_module=self._hashes_module,
                pbkdf2_cls=self._pbkdf2_cls,
            )
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


def _build_fernet(
    password: str,
    salt: bytes,
    iterations: int,
    fernet_cls: type[FernetType],
    hashes_module: Any,
    pbkdf2_cls: type[PBKDF2HMACType],
) -> FernetType:
    kdf = pbkdf2_cls(
        algorithm=hashes_module.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
    return fernet_cls(key)


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


def _import_crypto_components() -> tuple[
    type[FernetType],
    type[InvalidTokenType],
    Any,
    type[PBKDF2HMACType],
]:
    try:
        from cryptography.fernet import Fernet, InvalidToken
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "cryptography is required for encrypted storage. "
            "Install extras: pip install .[encrypt]"
        ) from exc
    return Fernet, InvalidToken, hashes, PBKDF2HMAC
