.PHONY: help setup run test lint format clean docker-build docker-run

help:
	@echo "Available commands:"
	@echo "  setup         : Set up the development environment"
	@echo "  run           : Run the application in development mode"
	@echo "  test          : Run tests"
	@echo "  lint          : Run linting checks"
	@echo "  format        : Format code"
	@echo "  clean         : Clean up temporary files"
	@echo "  docker-build  : Build Docker image"
	@echo "  docker-run    : Run with Docker"

setup:
	pip install -r requirements.txt
	mkdir -p data/documents data/chroma

run:
	python run.py

test:
	pytest

lint:
	flake8 app tests
	mypy app tests

format:
	black app tests
	isort app tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

docker-build:
	docker build -t rag-api .

docker-run:
	docker-compose up -d 