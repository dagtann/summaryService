.PHONY: install install-dev test test-unit test-integration lint format type-check clean run docker-build docker-run

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

# Testing
test: test-unit test-integration

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing

# Code Quality
lint:
	flake8 src tests

format:
	black src tests

format-check:
	black --check src tests

type-check:
	mypy src

# Development
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

run:
	python main.py

# Docker
docker-build:
	docker build -t summary-service .

docker-run:
	docker run -p 8000:8000 --env-file .env summary-service

# CI Pipeline
ci: install-dev lint type-check test-coverage