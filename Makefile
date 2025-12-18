# --- Configuration ---
BINARY_NAME = maxx-wp
PYTHON      = python
MAIN        = main.py
BUILD_FLAGS = --noconfirm --onefile --console --collect-all "paramiko" --collect-all "cryptography" --clean

# Default target (shows help)
.DEFAULT_GOAL := help

# --- Infrastructure ---

.PHONY: up
up: ## Spin up Docker infrastructure and bootstrap WordPress
	docker compose up -d --build
	@echo "Waiting for SSH to initialize..."
	@sleep 5
	$(PYTHON) $(MAIN) --clean --setup

.PHONY: down
down: ## Stop and remove Docker containers and volumes
	docker compose down -v

# --- Application Logic ---

.PHONY: maint
maint: ## Trigger remote updates and database optimization
	$(PYTHON) $(MAIN) --update --optimize

.PHONY: check
check: ## Run a standard health check and generate report
	$(PYTHON) $(MAIN)

.PHONY: all
all: up check ## Full lifecycle: Up -> Check -> Interactive Cleanup
	@echo ""
	@read -p "Lifecycle complete. Run 'make clean' now? [y/N] " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		$(MAKE) clean; \
	else \
		echo "Cleanup skipped. Stopping containers."; \
		$(MAKE) down; \
	fi

# --- Environment & Dependency Management ---

.PHONY: setup
setup: ## Initialize environment and sync dependencies using uv
	@echo "Installing project dependencies..."
	uv pip install -r requirements.txt || uv pip install paramiko cryptography pyinstaller

.PHONY: deps
deps: ## Freeze current environment into requirements.txt
	@echo "Freezing dependencies with uv..."
	uv pip freeze | grep -v "@ file://" > requirements.txt

# --- Distribution & Cleanup ---

.PHONY: dist
dist: ## Build a portable production binary (Linux/Windows)
	@echo "🚀 Building production binary with uv..."
	uv run pyinstaller $(BUILD_ALL) $(BUILD_FLAGS) --name $(BINARY_NAME) $(MAIN)
	@echo "✅ Build complete: ./dist/$(BINARY_NAME)"

.PHONY: dist-clean
dist-clean: ## Remove build artifacts and .spec files
	rm -rf build/ dist/ $(BINARY_NAME).spec

.PHONY: clean
clean: down dist-clean ## Full wipe: Stop Docker and delete logs/builds
	rm -rf logs/
	@echo "Environment fully reset."

# --- Utilities ---

.PHONY: help
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
