SRC_PATHS := \
    website_monitor/ tests/

.PHONY: wheel
wheel:
	python setup.py sdist bdist_wheel

.PHONY: run
run: wheel
	docker-compose up --build

.PHONY: tests
tests:
	pytest -svv tests/

.PHONY: format
format:
	isort $(SRC_PATHS)
	black $(SRC_PATHS)

.PHONY: lint
lint:
	isort -c ${SRC_PATHS}
	black --check $(SRC_PATHS)
	flake8 $(SRC_PATHS)

.PHONY: compile_protobuf
compile_protobuf:
	protoc -I protobuf --python_out=website_monitor/ protobuf/website_availability_metrics.proto --experimental_allow_proto3_optional
