# Contributing

Thanks for contributing. This project aims for clarity, test coverage, and safe defaults.

## Setup

```bash
pip install -r requirements-dev.txt
pre-commit install
```

## Local Checks

```bash
ruff check .
black --check .
mypy todo_app
pytest --maxfail=1 --disable-warnings -q --cov=todo_app
```

## Pull Requests

- Keep changes focused and well-documented.
- Update tests and docs for user-facing changes.
- Ensure CI passes before requesting review.
