# ------------ Settings ------------
PY           ?= poetry run
PKG          ?= async_websocket_pool
TESTS        ?= tests
SRC          ?= $(PKG) $(TESTS)

# Default goal
.DEFAULT_GOAL := help

# ------------ Targets -------------
.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		sed -E 's/:.*## /:\t/' | sort | column -s $$'\t' -t

.PHONY: install
install: ## Install project deps via Poetry
	poetry install

.PHONY: hooks
hooks: ## Install pre-commit hooks
	pre-commit install

.PHONY: format
format: ## Auto-fix imports & lint with Ruff, then format code
	$(PY) ruff check --fix $(SRC)
	$(PY) ruff format $(SRC)

.PHONY: lint
lint: ## Lint (no changes) with Ruff
	$(PY) ruff check $(SRC)

.PHONY: type
type: ## Type-check with mypy
	$(PY) mypy $(PKG)

.PHONY: test
test: ## Run tests with pytest
	$(PY) pytest -q

.PHONY: coverage
coverage: ## Run tests with coverage (terminal + XML)
	$(PY) pytest --cov=$(PKG) --cov-report=term-missing --cov-report=xml

.PHONY: check
check: ## CI-friendly: format check + lint + type + tests
	$(PY) ruff format --check $(SRC)
	$(PY) ruff check $(SRC)
	$(PY) mypy $(PKG)
	$(PY) pytest -q

.PHONY: clean
clean: ## Remove caches and build artifacts
	rm -rf .mypy_cache .ruff_cache .pytest_cache .coverage coverage.xml dist build
	find . -name '__pycache__' -type d -exec rm -rf {} +
