# FitForge developer Makefile
#
# Wraps the most common commands so contributors don't have to remember
# the long ``python manage.py …`` and ``docker compose …`` invocations.
#
# Run ``make help`` to see the full list of targets.

SHELL := /usr/bin/env bash
PY    := .venv/bin/python
PIP   := .venv/bin/pip
MANAGE := $(PY) manage.py
COVERAGE_THRESHOLD := 80

# Allow ``make manage ARGS='migrate'`` to invoke manage.py with extras.
ifeq ($(OS),Windows_NT)
PY    := .venv\Scripts\python.exe
PIP   := .venv\Scripts\pip.exe
MANAGE := $(PY) manage.py
endif

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install dev + test dependencies into the active venv.
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements/development.txt
	$(PIP) install -r requirements/test.txt

.PHONY: migrate
migrate: ## Apply database migrations.
	$(MANAGE) migrate --no-input

.PHONY: makemigrations
makemigrations: ## Generate new migration files.
	$(MANAGE) makemigrations

.PHONY: runserver
runserver: ## Start the Django dev server.
	$(MANAGE) runserver 0.0.0.0:8000

.PHONY: worker
worker: ## Start the Celery worker (requires Redis running).
	celery -A config worker -l INFO --concurrency=2

.PHONY: test
test: ## Run the test suite with coverage (fails under $(COVERAGE_THRESHOLD)%).
	DJANGO_SETTINGS_MODULE=config.settings.test \
	coverage run --source=apps,core $(MANAGE) test --verbosity=2
	coverage report --fail-under=$(COVERAGE_THRESHOLD)

.PHONY: test-fast
test-fast: ## Run tests without coverage (faster feedback loop).
	DJANGO_SETTINGS_MODULE=config.settings.test $(MANAGE) test --verbosity=1

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report and open it.
	DJANGO_SETTINGS_MODULE=config.settings.test \
	coverage run --source=apps,core $(MANAGE) test
	coverage html
	open htmlcov/index.html 2>/dev/null || start htmlcov\index.html

.PHONY: lint
lint: ## Run ruff lint and format checks.
	ruff check .
	ruff format --check .

.PHONY: format
format: ## Auto-format the codebase with ruff.
	ruff check . --fix
	ruff format .

.PHONY: collectstatic
collectstatic: ## Collect static files into STATIC_ROOT.
	$(MANAGE) collectstatic --no-input

.PHONY: shell
shell: ## Open a Django shell.
	$(MANAGE) shell

.PHONY: createsuperuser
createsuperuser: ## Create a superuser interactively.
	$(MANAGE) createsuperuser

.PHONY: docker-up
docker-up: ## Build and start the docker-compose stack.
	docker compose up --build -d

.PHONY: docker-down
docker-down: ## Stop the docker-compose stack.
	docker compose down

.PHONY: docker-logs
docker-logs: ## Tail logs from the docker-compose stack.
	docker compose logs -f

.PHONY: docker-shell
docker-shell: ## Open a shell in the running web container.
	docker compose exec web bash

.PHONY: k8s-validate
k8s-validate: ## Validate the Kubernetes manifests with Kustomize.
	kubectl kustomize k8s/overlays/production > /tmp/fitforge-prod.yaml
	kubectl apply --dry-run=client -f /tmp/fitforge-prod.yaml

.PHONY: k8s-apply-staging
k8s-apply-staging: ## Apply the staging overlay.
	kubectl apply -k k8s/overlays/staging

.PHONY: k8s-apply-prod
k8s-apply-prod: ## Apply the production overlay.
	kubectl apply -k k8s/overlays/production

.PHONY: clean
clean: ## Remove build artefacts and caches.
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type f -name "*.pyc" -delete 2>/dev/null; true
	rm -rf .coverage htmlcov/ coverage.xml .ruff_cache/ .mypy_cache/
