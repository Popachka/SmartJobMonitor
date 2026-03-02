IMAGE_NAME = job_monitor
PYTHON_MAIN = app.main
PROJECT_DIR = app
TEST_DIR = test
VENV_DIR = .venv
LOGFIRE_PROJECT = jobmonitor

.PHONY: help venv install run lint format test test-unit test-integration clean \
	docker-build docker-up docker-down docker-logs \
	obs-up obs-down obs-logs \
	logfire-auth logfire-use-project

default: help

help:
	@echo "Available make commands:"
	@echo "  venv              - Create a virtual environment (uv)"
	@echo "  install           - Install project dependencies (uv sync)"
	@echo "  run               - Run the app locally"
	@echo "  lint              - Run ruff + mypy"
	@echo "  format            - Auto-format with ruff"
	@echo "  test              - Run all tests"
	@echo "  test-unit         - Run unit tests"
	@echo "  test-integration  - Run integration tests"
	@echo "  clean             - Delete temporary files and caches"
	@echo "  docker-build      - Build Docker image"
	@echo "  docker-up         - Launch via docker compose"
	@echo "  docker-down       - Stop docker compose"
	@echo "  docker-logs       - View docker logs (SERVICE=...)"
	@echo "  obs-up            - Launch observability stack"
	@echo "  obs-down          - Stop observability stack"
	@echo "  obs-logs          - View observability logs (SERVICE=...)"
	@echo "  logfire-auth      - Authenticate Logfire locally"
	@echo "  logfire-use-project - Select Logfire project ($(LOGFIRE_PROJECT))"

venv:
	uv venv $(VENV_DIR)

install:
	uv sync

run:
	uv run -m $(PYTHON_MAIN)

lint:
	@echo "Starting checks..."
	uv run python -m ruff check $(PROJECT_DIR) $(TEST_DIR)
	uv run python -m mypy $(PROJECT_DIR)
	@echo "Checks completed!"

format:
	uv run python -m ruff format $(PROJECT_DIR) $(TEST_DIR)

test:
	uv run -m pytest -q

test-unit:
	uv run -m pytest $(TEST_DIR)/unit -q

test-integration:
	uv run -m pytest $(TEST_DIR)/integration -q

clean:
	@echo "Start cleaning..."
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm -rf .mypy_cache .ruff_cache .pytest_cache .egg-info
	@echo "Cleaning done!"

docker-build:
	docker build -t $(IMAGE_NAME) .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f $(SERVICE)

obs-up:
	docker compose -f docker-compose.observability.yml up -d

obs-down:
	docker compose -f docker-compose.observability.yml down

obs-logs:
	docker compose -f docker-compose.observability.yml logs -f $(SERVICE)

logfire-auth:
	uv run logfire auth

logfire-use-project:
	uv run logfire projects use $(LOGFIRE_PROJECT)
