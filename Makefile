
.PHONY: build_container
build_container:
	docker-compose build

.PHONY: run_containers
run_containers:
	docker-compose up -d

.PHONY: stop_containers
stop_containers:
	docker-compose down

.PHONY: clean
clean_containers:
	docker-compose down --rmi all --volumes --remove-orphans

.PHONY: run_tests
run_tests:
	docker-compose -f docker-compose-test.yml run --rm test

dev_create_db:
	docker-compose -f docker-compose-dev.yml run create_dev_db

dev_bootstrap_db:
	docker-compose -f docker-compose-dev.yml run bootstrap_db

dev_new_migration:
	docker-compose -f docker-compose-dev.yml run alembic_migrate

dev_run_migrations:
	docker-compose -f docker-compose-dev.yml run alembic_upgrade

dev_local_new_migration:
	alembic revision --autogenerate -m "Migration"

dev_local_run_migrations:
	alembic upgrade head