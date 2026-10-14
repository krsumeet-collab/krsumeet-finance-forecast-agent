.PHONY: setup test eval lint run docker-build docker-run clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
UVICORN = $(VENV)/bin/uvicorn
RUFF = $(VENV)/bin/ruff
MYPY = $(VENV)/bin/mypy

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	$(PIP) install -e ".[dev]"

lint:
	$(RUFF) check src/ tests/
	$(MYPY) src/

test:
	$(PYTEST) tests/ --cov=src --cov-fail-under=80 --cov-report=term-missing

eval:
	$(PYTHON) eval/run_eval.py

run:
	$(UVICORN) src.api.app:app --host 0.0.0.0 --port 8080 --reload

docker-build:
	docker build -t finance-forecast-agent:latest -f ci_cd/Dockerfile .

docker-run:
	docker run -p 8080:8080 -e ENVIRONMENT=dev finance-forecast-agent:latest

clean:
	rm -rf .pytest_cache .coverage htmlcov tests/coverage_html __pycache__ src/**/__pycache__
