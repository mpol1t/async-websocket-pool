# Contributing

## Development Setup

1. Install Poetry.
2. Run `poetry install`.
3. Run `poetry run pre-commit install` if you want local hooks.

## Common Commands

- `poetry run pytest -q`
- `poetry run ruff check .`
- `poetry run ruff format .`
- `poetry run mypy async_websocket_pool`
- `make check`

## Pull Requests

- Keep changes focused.
- Add or update tests for behavior changes.
- Update `README.md` or `CHANGELOG.md` when the user-facing behavior changes.
- Make sure local checks pass before opening a pull request.

## Release Notes

- Add notable user-facing changes to `CHANGELOG.md`.
- Keep entries short and release-oriented.
