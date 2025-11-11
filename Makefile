.PHONY: help setup dev docker-up docker-down docker-build docker-logs clean test lint

# Default target
help:
	@echo "Available commands:"
	@echo "  make setup        - Initial project setup with Docker"
	@echo "  make dev          - Run development servers locally"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make docker-build - Rebuild Docker containers"
	@echo "  make docker-logs  - View Docker logs"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"

# Setup project
setup:
	@./setup.sh

# Run development servers
dev:
	@./dev.sh

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf backend/__pycache__ backend/.pytest_cache backend/.coverage
	@rm -rf frontend/node_modules frontend/.next frontend/out
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@echo "Clean complete!"

# Run tests
test:
	@echo "Running backend tests..."
	@cd backend && python -m pytest
	@echo "Running frontend tests..."
	@cd frontend && npm test

# Run linters
lint:
	@echo "Linting backend..."
	@cd backend && python -m flake8 src/
	@echo "Linting frontend..."
	@cd frontend && npm run lint