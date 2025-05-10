.PHONY: test-db test test-reset test-runner prod-db prod-reset prod reset

# Build and run the test database in the background
test-db:
	docker compose -f docker-compose.test.yml up -d --build

# Run the test runner once
test-runner:
	docker compose -f docker-compose.test.yml run --rm test-runner

# Run tests
test:
	PYTHONPATH=. pytest -v

# Reset the test environment (bring down and rebuild containers)
test-reset:
	docker compose -f docker-compose.test.yml down -v
	docker compose -f docker-compose.test.yml up -d --build
	docker compose -f docker-compose.test.yml run --rm test-runner

# Build and run the production database in the background
prod-db:
	docker compose -f docker-compose.yml up -d --build

# Reset the production environment (bring down and rebuild containers)
prod-reset:
	docker compose -f docker-compose.yml down -v
	docker compose -f docker-compose.yml up -d --build

# Start the production environment in the background
prod:
	docker compose -f docker-compose.yml up -d

# New reset target to handle both test and reset operations
reset: test-reset
	docker compose -f docker-compose.test.yml down -v
	docker compose -f docker-compose.test.yml up -d --build
	docker compose -f docker-compose.test.yml run --rm test-runner
