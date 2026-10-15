.PHONY: install dev test lint format up down

install:
	uv sync

dev:
	uv run uvicorn --factory issueflow.main:create_app --reload

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

format:
	uv run ruff check --fix .
	uv run ruff format .

up:
	docker compose up --build

down:
	docker compose down
