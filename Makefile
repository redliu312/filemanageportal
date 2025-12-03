.PHONY: help setup docker-up docker-down docker-build docker-logs docker-db-init supabase-up supabase-down supabase-db-init clean test lint

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "Docker Development (Local PostgreSQL):"
	@echo "  make setup           - Initial project setup with Docker"
	@echo "  make docker-up       - Start Docker containers"
	@echo "  make docker-down     - Stop Docker containers"
	@echo "  make docker-build    - Rebuild Docker containers"
	@echo "  make docker-logs     - View Docker logs"
	@echo "  make docker-db-init  - Initialize database tables"
	@echo ""
	@echo "Docker Development (Supabase Backend):"
	@echo "  make supabase-up     - Start with Supabase backend"
	@echo "  make supabase-down   - Stop Supabase containers"
	@echo "  make supabase-db-init - Initialize Supabase database"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make test            - Run tests"
	@echo "  make lint            - Run linters"

# Setup project
setup:
	@./setup.sh

# Docker commands
docker-up:
	docker-compose up

docker-down:
	docker-compose down

docker-build:
	docker-compose build --no-cache

docker-logs:
	docker-compose logs -f

# Initialize database
docker-db-init:
	@echo "Initializing database tables..."
	docker-compose exec backend sh -c ". /app/.venv/bin/activate && python manage.py init"
	@echo "Database initialization complete!"

# Supabase commands
supabase-up:
	@echo "Starting services with Supabase backend..."
	docker-compose -f docker-compose.supabase.yml up -d

supabase-down:
	@echo "Stopping Supabase services..."
	docker-compose -f docker-compose.supabase.yml down

supabase-db-init:
	@echo "Initializing Supabase database tables..."
	docker-compose -f docker-compose.supabase.yml exec backend sh -c ". /app/.venv/bin/activate && python manage.py init"
	@echo "Supabase database initialization complete!"

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