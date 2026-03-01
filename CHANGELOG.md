# Changelog

All notable changes to this project will be documented in this file.

The history below is based on git tags and the commits between them.

## [Unreleased]

## [0.3.0] - 2026-03-01

### Added
- Applied backpressure to message handling so handler concurrency is bounded.
- Drained in-flight handler tasks before reconnecting.
- Added bounded reconnect cleanup for pending handlers.

### Changed
- Documented handler drain and cancellation semantics.
- Updated Ruff through the latest merged Dependabot updates on `main`.

## [0.2.0] - 2025-11-09

### Added
- Added a `Makefile` for common development commands.
- Added pre-commit configuration and CI execution for repository checks.
- Added a broader test suite around the websocket pool behavior.
- Added a Code of Conduct.

### Changed
- Updated the websocket pool implementation and refreshed project tooling.
- Revised GitHub Actions naming and refreshed README badges.
- Bumped the package version to `0.2.0`.

## [0.1.10] - 2025-09-13

### Changed
- Added workflow permissions to address code scanning findings.
- Bumped the package version to `0.1.10`.
- Continued routine dependency maintenance for `coverage`, `pytest`, `pytest-cov`, and `pytest-asyncio`.

## [0.1.9] - 2024-09-21

### Changed
- Updated the PyPI publish workflow configuration.
- Adjusted project metadata in `pyproject.toml`.
- Continued dependency maintenance for `websockets`, `pytest`, and `pytest-asyncio`.

## [0.1.8] - 2024-09-21

### Changed
- Bumped the package minor version to `0.1.8`.

## [0.1.7] - 2024-03-28

### Changed
- Split runtime and development dependencies in `pyproject.toml`.
- Updated CI and PyPI workflow configuration.
- Introduced Dependabot configuration for automated dependency updates.
- Upgraded core dependencies including `websockets`, `pytest`, and `pytest-asyncio`.

## [0.1.6] - 2023-06-11

### Fixed
- Removed default logging configuration from the library.
- Added missing connect docstring details.

## [0.1.4] - 2023-05-23

### Added
- Added the `on_connect` callback to `connect()`.
- Refactored `connect()` to support coroutine handlers and bounded task execution with a semaphore.

### Changed
- Renamed `message_handler` to `on_message`.
- Expanded tests and refreshed documentation for the callback model.

## [0.1.0] - 2023-05-15

### Added
- Initial package implementation.
- Initial repository setup, test dependencies, CI workflow, and README.
