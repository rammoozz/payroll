.PHONY: help up down logs test clean

help:
	@echo "Available commands:"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make test     - Run all tests"
	@echo "  make clean    - Clean up containers and volumes"

up:
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 5
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	@echo "Running backend unit tests..."
	docker-compose exec backend pytest
	@echo "Backend tests complete!"

clean:
	docker-compose down -v
	rm -rf storage/*
	@echo "Cleanup complete!"

# Development helpers
backend-shell:
	docker-compose exec backend /bin/bash

db-shell:
	docker-compose exec postgres psql -U payroll_user -d payroll

celery-logs:
	docker-compose logs -f worker