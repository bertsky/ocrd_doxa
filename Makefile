PYTHON = python3
PIP = pip3
PYTHONIOENCODING=utf8
PYTEST_ARGS = -vv

DOCKER_BASE_IMAGE = docker.io/ocrd/core:v3.3.0
DOCKER_TAG = ocrd/doxa

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    deps         pip install -r requirements.txt"
	@echo "    install      pip install ."
	@echo "    install-dev  pip install -e ."
	@echo "    deps-test    pip install -r requirements_test.txt"
	@echo "    test         python -m pytest test"
	@echo "    tests/assets prepare test assets"
	@echo "    build        python -m build ."
	@echo "    docker       build Docker image"
	@echo ""
	@echo "  Variables"
	@echo "    PYTHON       name of the Python binary [$(PYTHON)]"
	@echo "    PIP          name of the Python packager [$(PIP)]"
	@echo "    DOCKER_TAG   name of the Docker image [$(DOCKER_TAG)]"
	@echo "    PYTEST_ARGS  extra runtime arguments for test [$(PYTEST_ARGS)]"
	@echo ""

# Install Python deps via pip
deps:
	$(PIP) install -r requirements.txt

deps-test:
	$(PIP) install -r requirements_test.txt

# Install Python package via pip
install:
	$(PIP) install .

install-dev:
	$(PIP) install -e .

build:
	$(PIP) install build wheel
	$(PYTHON) -m build .

# Ensure assets and olena git repos are always on the correct revision:
.PHONY: always-update

# Checkout OCR-D/assets submodule to ./repo/assets
repo/assets: always-update
	git submodule sync "$@"
	git submodule update --init "$@"

# Copy index of assets
tests/assets: repo/assets
	mkdir -p $@
	git -C repo/assets checkout-index -a -f --prefix=$(abspath $@)/
	touch $@/__init__.py

# Run tests
test: tests/assets deps-test
	$(PYTHON) -m pytest tests --durations=0 --continue-on-collection-errors $(PYTEST_ARGS)

coverage: deps-test
	coverage erase
	$(MAKE) test PYTHON="coverage run"
	coverage combine
	coverage report -m

docker:
	docker build \
	--build-arg DOCKER_BASE_IMAGE=$(DOCKER_BASE_IMAGE) \
	--build-arg VCS_REF=$$(git rev-parse --short HEAD) \
	--build-arg BUILD_DATE=$$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
	-t $(DOCKER_TAG) .

.PHONY: help build coverage deps deps-test docker install install-dev test
