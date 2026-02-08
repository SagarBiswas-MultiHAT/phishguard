# Developer Guide

## Storage Backends

1. Create a new module in `todo_app/` that implements the `Storage` interface.
2. Implement `load_tasks()` and `save_tasks()` with atomic or transactional safety.
3. Add any required configuration to `todo_app/cli.py`.
4. Add tests in `tests/` that cover roundtrip and failure cases.

## Running Tests Locally

```bash
pip install -r requirements-dev.txt
pytest --maxfail=1 --disable-warnings -q --cov=todo_app
```

## CI Locally

```bash
tox
```
