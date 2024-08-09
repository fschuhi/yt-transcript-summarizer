
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

run_alembic_test_database:
	docker-compose -f docker-compose-test.yml run alembic

