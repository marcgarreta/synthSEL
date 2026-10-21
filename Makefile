.PHONY: install test lint format cov

install:
	uv sync

test:
	uv run pytest -m "not slow"

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

cov:
	uv run pytest -m "not slow" --cov --cov-report=term-missing --cov-report=html
