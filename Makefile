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

# Allow ``make manage ARGS='migrate'`` to invoke manage.py with extras.
ifeq ($(OS),Windows_NT)
PY    := .venv\Scripts\python.exe
PIP   := .venv\Scripts\pip.exe
MANAGE := $(PY) manage.py
endif

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install dev dependencies into the active venv.
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

.PHONY: test
test: ## Run the test suite with coverage.
	coverage run --source=apps,core $(MANAGE) test --verbosity=2
	coverage report --fail-under=70

.PHONY: lint
lint: ## Run ruff lint and format checks.
	$(PIP) install ruff
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

.PHONY: docker-up
docker-up: ## Build and start the docker-compose stack.
	docker compose up --build -d

.PHONY: docker-down
docker-down: ## Stop the docker-compose stack.
	docker compose down

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
