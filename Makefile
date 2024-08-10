
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

boostrap_dev_db:
	docker-compose -f docker-compose-dev.yml run bootstrap_db

create_new_dev_migration:
	docker-compose -f docker-compose-dev.yml run alembic_migrate

run_dev_migrations:
	docker-compose -f docker-compose-dev.yml run alembic_upgrade
