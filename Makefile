
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
clean:
	docker-compose down --rmi all --volumes --remove-orphans

.PHONY: run_tests
run_tests:
	docker-compose run --rm test
