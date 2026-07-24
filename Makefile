# Developer convenience targets. All tools run through `uv run` against the
# project .venv. Flags mirror tox.ini so `make lint` matches the CI lint env.

.DEFAULT_GOAL := help

BLACK_EXCLUDE := ./env|gspread/__init__.py
CODESPELL_SKIP := .tox,.git,./docs/build,.mypy_cache,./env

# Extra args passed through to pytest, e.g. `make test ARGS="tests/cell_test.py -x"`
ARGS ?=

.PHONY: help install test lint format black flake8 isort codespell mypy build clean

help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Create the .venv (Python 3.14.6) and install runtime + test + lint deps
	uv venv --python 3.14.6
	uv pip install -e . -r test-requirements.txt -r lint-requirements.txt

test: ## Run the offline test suite (ARGS=... passthrough to pytest)
	uv run pytest tests/ $(ARGS)

lint: black flake8 isort codespell mypy ## Run the full lint suite (matches CI)

format: ## Auto-format code with black and isort
	uv run black --extend-exclude="$(BLACK_EXCLUDE)" .
	uv run isort .

black: ## Check formatting with black
	uv run black --check --diff --extend-exclude="$(BLACK_EXCLUDE)" .

flake8: ## Run flake8
	uv run flake8 .

isort: ## Check import ordering with isort
	uv run isort --check-only .

codespell: ## Check spelling with codespell
	uv run codespell --skip="$(CODESPELL_SKIP)" .

mypy: ## Run mypy type checks
	uv run mypy --install-types --non-interactive --ignore-missing-imports ./gspread ./tests

build: ## Build the sdist and wheel
	uv build

clean: ## Remove caches and build artifacts
	rm -rf .mypy_cache .pytest_cache dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
