# PyLama Ecosystem Makefile with Integrated Logging
# This Makefile ensures LogLama starts first to capture logs from all services

ROOT_DIR := ..

# Default values for environment variables
PORT ?= 8080
HOST ?= 127.0.0.1

# Port assignments for each service
LOGLAMA_PORT ?= 5001
BEXY_PORT ?= 8000
GETLLM_PORT ?= 8001
SHELLAMA_PORT ?= 8002
DEVLAMA_PORT ?= 8003
APILAMA_PORT ?= 8080
WEBLAMA_PORT ?= 8084

# Log directory and database path
LOG_DIR ?= ./logs
DB_PATH ?= $(LOG_DIR)/loglama.db

# Colors for better output
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
RED := \033[0;31m
NC := \033[0m # No Color

.PHONY: all setup clean test test-makefiles test-makefiles-docker test-github-actions validate-github-actions lint format run-all run-loglama run-collector run-bexy run-getllm run-devlama run-apilama run-shellama run-weblama stop-all stop status help

# Default target
all: help

# Setup all projects with virtual environments
setup: setup-loglama setup-bexy setup-getllm setup-devlama setup-apilama setup-shellama setup-weblama
	@echo "\n$(GREEN)All services have been set up successfully!$(NC)"

# Setup individual projects with virtual environments
setup-loglama:
	@echo "$(BLUE)Setting up LogLama (Logging Service)...$(NC)"
	cd $(ROOT_DIR)/loglama && python -m venv venv && . venv/bin/activate && pip install -e .

setup-bexy:
	@echo "$(BLUE)Setting up BEXY...$(NC)"
	cd $(ROOT_DIR)/bexy && python -m venv venv && . venv/bin/activate && pip install -e .

setup-getllm:
	@echo "$(BLUE)Setting up PyLLM...$(NC)"
	cd $(ROOT_DIR)/getllm && python -m venv venv && . venv/bin/activate && pip install -e .

setup-devlama:
	@echo "$(BLUE)Setting up PyLama (Central Orchestration Service)...$(NC)"
	cd $(ROOT_DIR)/devlama && python -m venv venv && . venv/bin/activate && pip install -e .

setup-apilama:
	@echo "$(BLUE)Setting up APILama (API Gateway)...$(NC)"
	cd $(ROOT_DIR)/apilama && python -m venv venv && . venv/bin/activate && pip install -e .

setup-shellama:
	@echo "$(BLUE)Setting up SheLLama (Shell Operations)...$(NC)"
	cd $(ROOT_DIR)/shellama && python -m venv venv && . venv/bin/activate && pip install -e .

setup-weblama:
	@echo "$(BLUE)Setting up WebLama (Frontend)...$(NC)"
	cd $(ROOT_DIR)/weblama && npm install

# Create logs directory
create-logs-dir:
	@mkdir -p $(LOG_DIR)
	@echo "$(BLUE)Created logs directory at $(LOG_DIR)$(NC)"

# Reset LogLama database to ensure proper schema
reset-loglama-db: create-logs-dir
	@rm -f $(DB_PATH)
	@echo "$(BLUE)Reset LogLama database at $(DB_PATH)$(NC)"

# Run LogLama web interface (must run first to capture logs)
run-loglama: reset-loglama-db
	@echo "$(BLUE)Starting LogLama web interface on $(HOST):$(LOGLAMA_PORT)...$(NC)"
	@cd $(ROOT_DIR)/loglama && . venv/bin/activate && python -m loglama.cli.main web --host $(HOST) --port $(LOGLAMA_PORT) --db $(DB_PATH) & echo $$! > $(LOG_DIR)/loglama.pid
	@echo "$(GREEN)LogLama web interface started with PID $$(cat $(LOG_DIR)/loglama.pid)$(NC)"
	@echo "$(GREEN)LogLama web interface available at http://$(HOST):$(LOGLAMA_PORT)$(NC)"
	@sleep 2 # Give LogLama time to initialize

# Run LogLama collector daemon
run-collector: create-logs-dir
	@echo "$(BLUE)Starting LogLama collector daemon...$(NC)"
	@cd $(ROOT_DIR)/loglama && . venv/bin/activate && python -m loglama.cli.main collect-daemon --background
	@echo "$(GREEN)LogLama collector daemon started$(NC)"
	@sleep 1 # Give collector time to initialize

# Run BEXY service
run-bexy: create-logs-dir
	@echo "$(BLUE)Starting BEXY on $(HOST):$(BEXY_PORT)...$(NC)"
	@cd $(ROOT_DIR)/bexy && . venv/bin/activate && PORT=$(BEXY_PORT) HOST=$(HOST) python -m bexy.api.server & echo $$! > $(LOG_DIR)/bexy.pid
	@echo "$(GREEN)BEXY started with PID $$(cat $(LOG_DIR)/bexy.pid)$(NC)"
	@echo "$(GREEN)BEXY available at http://$(HOST):$(BEXY_PORT)$(NC)"

# Run PyLLM service
run-getllm: create-logs-dir
	@echo "$(BLUE)Starting PyLLM on $(HOST):$(GETLLM_PORT)...$(NC)"
	@cd $(ROOT_DIR)/getllm && PORT=$(GETLLM_PORT) HOST=$(HOST) poetry run getllm & echo $$! > $(LOG_DIR)/getllm.pid
	@echo "$(GREEN)PyLLM started with PID $$(cat $(LOG_DIR)/getllm.pid)$(NC)"
	@echo "$(GREEN)PyLLM available at http://$(HOST):$(GETLLM_PORT)$(NC)"

# Run SheLLama service
run-shellama: create-logs-dir
	@echo "$(BLUE)Starting SheLLama on $(HOST):$(SHELLAMA_PORT)...$(NC)"
	@cd $(ROOT_DIR)/shellama && . venv/bin/activate && PORT=$(SHELLAMA_PORT) HOST=$(HOST) python -m shellama.api.server & echo $$! > $(LOG_DIR)/shellama.pid
	@echo "$(GREEN)SheLLama started with PID $$(cat $(LOG_DIR)/shellama.pid)$(NC)"
	@echo "$(GREEN)SheLLama available at http://$(HOST):$(SHELLAMA_PORT)$(NC)"

# Run PyLama service
run-devlama: create-logs-dir
	@echo "$(BLUE)Starting PyLama on $(HOST):$(DEVLAMA_PORT)...$(NC)"
	@cd $(ROOT_DIR)/devlama && . venv/bin/activate && PORT=$(DEVLAMA_PORT) HOST=$(HOST) python -m devlama.api.server & echo $$! > $(LOG_DIR)/devlama.pid
	@echo "$(GREEN)PyLama started with PID $$(cat $(LOG_DIR)/devlama.pid)$(NC)"
	@echo "$(GREEN)PyLama available at http://$(HOST):$(DEVLAMA_PORT)$(NC)"

# Run APILama service
run-apilama: create-logs-dir
	@echo "$(BLUE)Starting APILama on $(HOST):$(APILAMA_PORT)...$(NC)"
	@cd $(ROOT_DIR)/apilama && . venv/bin/activate && PORT=$(APILAMA_PORT) HOST=$(HOST) python -m apilama.api.server & echo $$! > $(LOG_DIR)/apilama.pid
	@echo "$(GREEN)APILama started with PID $$(cat $(LOG_DIR)/apilama.pid)$(NC)"
	@echo "$(GREEN)APILama available at http://$(HOST):$(APILAMA_PORT)$(NC)"

# Run WebLama service with log collection enabled
run-weblama: create-logs-dir
	@echo "$(BLUE)Starting WebLama on $(HOST):$(WEBLAMA_PORT)...$(NC)"
	@cd $(ROOT_DIR)/weblama && PORT=$(WEBLAMA_PORT) HOST=$(HOST) COLLECT=1 make web & echo $$! > $(LOG_DIR)/weblama.pid
	@echo "$(GREEN)WebLama started with PID $$(cat $(LOG_DIR)/weblama.pid)$(NC)"
	@echo "$(GREEN)WebLama available at http://$(HOST):$(WEBLAMA_PORT)$(NC)"

# Run all services in the correct order with LogLama first
run-all: run-loglama run-collector run-bexy run-getllm run-shellama run-devlama run-apilama run-weblama
	@echo "\n$(GREEN)All PyLama services are now running!$(NC)"
	@echo "$(GREEN)LogLama web interface: http://$(HOST):$(LOGLAMA_PORT)$(NC)"
	@echo "$(GREEN)WebLama interface: http://$(HOST):$(WEBLAMA_PORT)$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to stop all services or use 'make stop-all'$(NC)"

# Open LogLama in the browser
open-loglama:
	@echo "$(BLUE)Opening LogLama in browser...$(NC)"
	@python -m webbrowser "http://$(HOST):$(LOGLAMA_PORT)"

# Open WebLama in the browser
open-weblama:
	@echo "$(BLUE)Opening WebLama in browser...$(NC)"
	@python -m webbrowser "http://$(HOST):$(WEBLAMA_PORT)"

# Open both LogLama and WebLama in the browser
open-all: open-loglama open-weblama
	@echo "$(GREEN)Opened both LogLama and WebLama in browser$(NC)"

# Stop all services
stop-all:
	@echo "$(BLUE)Stopping all PyLama services...$(NC)"
	@for pid_file in $(LOG_DIR)/*.pid; do \
		if [ -f "$$pid_file" ]; then \
			pid=$$(cat $$pid_file); \
			service=$$(basename $$pid_file .pid); \
			echo "$(YELLOW)Stopping $$service (PID: $$pid)...$(NC)"; \
			kill $$pid 2>/dev/null || true; \
			rm -f $$pid_file; \
		fi \
	done
	@echo "$(GREEN)All services stopped$(NC)"

# Alias for stop-all
stop: stop-all

# Check status of all services
status:
	@echo "$(BLUE)PyLama Ecosystem Status:$(NC)"
	@for pid_file in $(LOG_DIR)/*.pid; do \
		if [ -f "$$pid_file" ]; then \
			pid=$$(cat $$pid_file); \
			service=$$(basename $$pid_file .pid); \
			if ps -p $$pid > /dev/null; then \
				echo "$(GREEN)$$service is running (PID: $$pid)$(NC)"; \
			else \
				echo "$(RED)$$service is not running (stale PID file)$(NC)"; \
			fi \
		fi \
	done
	@echo ""
	@echo "$(BLUE)Service URLs:$(NC)"
	@echo "$(GREEN)LogLama: http://$(HOST):$(LOGLAMA_PORT)$(NC)"
	@echo "$(GREEN)BEXY: http://$(HOST):$(BEXY_PORT)$(NC)"
	@echo "$(GREEN)PyLLM: http://$(HOST):$(GETLLM_PORT)$(NC)"
	@echo "$(GREEN)SheLLama: http://$(HOST):$(SHELLAMA_PORT)$(NC)"
	@echo "$(GREEN)PyLama: http://$(HOST):$(DEVLAMA_PORT)$(NC)"
	@echo "$(GREEN)APILama: http://$(HOST):$(APILAMA_PORT)$(NC)"
	@echo "$(GREEN)WebLama: http://$(HOST):$(WEBLAMA_PORT)$(NC)"

# Test all Makefiles in all projects
test-makefiles:
	@echo "$(BLUE)Testing all Makefiles in all projects...$(NC)"
	@cd $(ROOT_DIR) && ./test_all_makefiles.sh

# Test all Makefiles with verbose output
test-makefiles-verbose:
	@echo "$(BLUE)Testing all Makefiles in all projects with verbose output...$(NC)"
	@cd $(ROOT_DIR) && ./test_all_makefiles.sh --verbose

# Test all Makefiles in Docker containers
test-makefiles-docker:
	@echo "$(BLUE)Testing all Makefiles in Docker containers...$(NC)"
	@cd $(ROOT_DIR) && ./docker_test_makefiles.sh

# Test GitHub Actions workflows locally
test-github-actions:
	@echo "$(BLUE)Testing GitHub Actions workflows locally...$(NC)"
	@cd $(ROOT_DIR) && ./tests/test_github_actions.sh

# Validate GitHub Actions workflow files
validate-github-actions:
	@echo "$(BLUE)Validating GitHub Actions workflow files...$(NC)"
	@cd $(ROOT_DIR) && ./tests/validate_github_workflows.sh

# Fix GitHub Actions workflow files
fix-github-actions:
	@echo "$(BLUE)Fixing GitHub Actions workflow files...$(NC)"
	@cd $(ROOT_DIR) && ./tests/validate_github_workflows.sh --fix

# Run comprehensive tests for all projects
test-all: test-makefiles test-github-actions
	@echo "$(BLUE)Running comprehensive tests for all projects...$(NC)"
	@cd $(ROOT_DIR) && ./tests/run_all_tests.sh

# Clean all projects
clean: stop-all
	@echo "$(BLUE)Cleaning up all projects...$(NC)"
	@echo "$(YELLOW)Removing logs directory...$(NC)"
	@rm -rf $(LOG_DIR)
	@echo "$(YELLOW)Cleaning up Python cache files...$(NC)"
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name *.egg-info -exec rm -rf {} +
	@find . -type d -name .pytest_cache -exec rm -rf {} +
	@echo "$(GREEN)Cleanup completed$(NC)"

# Help target
help:
	@echo "$(BLUE)PyLama Ecosystem Makefile with Integrated Logging$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup Commands:$(NC)"
	@echo "  setup            - Set up all projects with virtual environments"
	@echo "  setup-loglama    - Set up LogLama only"
	@echo "  setup-bexy       - Set up BEXY only"
	@echo "  setup-getllm     - Set up PyLLM only"
	@echo "  setup-devlama    - Set up PyLama only"
	@echo "  setup-apilama    - Set up APILama only"
	@echo "  setup-shellama   - Set up SheLLama only"
	@echo "  setup-weblama    - Set up WebLama only"
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(NC)"
	@echo "  test-all              - Run comprehensive tests for all projects"
	@echo "  test-makefiles        - Test all Makefiles in all projects"
	@echo "  test-makefiles-verbose - Test all Makefiles with verbose output"
	@echo "  test-makefiles-docker - Test all Makefiles in Docker containers"
	@echo "  test-github-actions   - Test GitHub Actions workflows locally"
	@echo "  validate-github-actions - Validate GitHub Actions workflow files"
	@echo "  fix-github-actions    - Fix common issues in GitHub Actions workflows"
	@echo ""
	@echo "$(YELLOW)Run Commands:$(NC)"
	@echo "  run-all          - Run all services in the correct order with LogLama first"
	@echo "  run-loglama      - Run LogLama web interface on port $(LOGLAMA_PORT)"
	@echo "  run-collector    - Run LogLama collector daemon"
	@echo "  run-bexy        - Run BEXY on port $(BEXY_PORT)"
	@echo "  run-getllm        - Run PyLLM on port $(GETLLM_PORT)"
	@echo "  run-shellama     - Run SheLLama on port $(SHELLAMA_PORT)"
	@echo "  run-devlama       - Run PyLama on port $(DEVLAMA_PORT)"
	@echo "  run-apilama      - Run APILama on port $(APILAMA_PORT)"
	@echo "  run-weblama      - Run WebLama on port $(WEBLAMA_PORT)"
	@echo ""
	@echo "$(YELLOW)Browser Commands:$(NC)"
	@echo "  open-loglama     - Open LogLama in the browser"
	@echo "  open-weblama     - Open WebLama in the browser"
	@echo "  open-all         - Open both LogLama and WebLama in the browser"
	@echo ""
	@echo "$(YELLOW)Management Commands:$(NC)"
	@echo "  status           - Check status of all services"
	@echo "  stop-all         - Stop all running services"
	@echo "  clean            - Clean all projects and stop all services"
	@echo ""
	@echo "$(YELLOW)Usage Examples:$(NC)"
	@echo "  make run-all                      - Run all services with default ports"
	@echo "  make run-all LOGLAMA_PORT=5002    - Run all services with LogLama on port 5002"
	@echo "  make run-loglama run-weblama      - Run only LogLama and WebLama"
	@echo "  make test-makefiles               - Test all Makefiles in all projects"
	@echo "  make test-github-actions          - Test GitHub Actions workflows locally"
	@echo "  make status                       - Check which services are running"
	@echo "  make stop-all                     - Stop all running services"
