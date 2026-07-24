# Developer convenience targets. Individual lint tools run through `uv run`
# against the project .venv, with flags mirroring tox.ini, so `make lint`
# matches the tools in `tox -e lint`. `make ci` reproduces the full CI
# lint_python job (lint + tests + security + build + docs) via tox and uvx.

.DEFAULT_GOAL := help

BLACK_EXCLUDE := ./env|gspread/__init__.py
CODESPELL_SKIP := .tox,.git,./docs/build,.mypy_cache,./env,./.venv

# Extra args passed through to pytest, e.g. `make test ARGS="tests/cell_test.py -x"`
ARGS ?=

.PHONY: help install test lint format black flake8 isort codespell mypy bandit pyupgrade pip-audit doc build ci clean

help: ## Show this help
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Create the .venv (Python 3.14.6) and install runtime + test + lint deps
	uv venv --python 3.14.6
	uv pip install -e . -r test-requirements.txt -r lint-requirements.txt

test: ## Run the offline test suite (ARGS=... passthrough to pytest)
	uv run pytest tests/ $(ARGS)

lint: black flake8 isort codespell mypy ## Run the linters/formatters/type check (mirrors tox -e lint)

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

bandit: ## Run the bandit security scan (as CI does)
	uv run bandit --recursive --skip B105,B110,B311,B605,B607,B101 --exclude ./.tox,./.venv .

pyupgrade: ## Check for outdated Python syntax on tracked files (as CI does)
	uvx pyupgrade --py3-only $(shell git ls-files '*.py')

pip-audit: ## Audit dependencies for known vulnerabilities (as CI does; non-fatal)
	-uvx pip-audit --ignore-vuln PYSEC-2023-228 --ignore-vuln PYSEC-2022-43012 --ignore-vuln GHSA-5rjg-fvgr-3xxf --ignore-vuln GHSA-48p4-8xcf-vxj5 --ignore-vuln GHSA-pq67-6m6q-mj2v

doc: ## Build the documentation (mirrors tox -e doc)
	uvx --with tox-uv tox -e doc

build: ## Build the sdist and wheel
	uv build

ci: ## Reproduce the full CI lint_python job locally (lint + tests + security + build + docs)
	uv run bandit --recursive --skip B105,B110,B311,B605,B607,B101 --exclude ./.tox,./.venv .
	uvx --with tox-uv tox -e lint
	uvx --with tox-uv tox -e py
	uvx pyupgrade --py3-only $(shell git ls-files '*.py')
	-uvx pip-audit --ignore-vuln PYSEC-2023-228 --ignore-vuln PYSEC-2022-43012 --ignore-vuln GHSA-5rjg-fvgr-3xxf --ignore-vuln GHSA-48p4-8xcf-vxj5 --ignore-vuln GHSA-pq67-6m6q-mj2v
	uvx --with tox-uv tox -e build
	uvx --with tox-uv tox -e doc

clean: ## Remove caches and build artifacts
	rm -rf .mypy_cache .pytest_cache dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
