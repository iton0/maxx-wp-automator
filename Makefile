# --- Configuration ---
BINARY_NAME = maxx-wp
# 'uv run' ensures we use the project's exact Python 3.14 environment
PYTHON      = uv run python
MAIN        = main.py
BUILD_CMD   = uv run --group build pyinstaller
BUILD_FLAGS = --noconfirm --onefile --console --collect-all "paramiko" --collect-all "cryptography" --clean

# Default target
.DEFAULT_GOAL := help

# --- Infrastructure & Orchestration ---

.PHONY: up
up: ## [Infra] Spin up LAMP stack and bootstrap WordPress via SSH
	docker compose up -d --build
	@echo "Waiting for SSH to initialize..."
	@sleep 5
	$(PYTHON) $(MAIN) --clean --setup

.PHONY: down
down: ## [Infra] Teardown containers and wipe volumes
	docker compose down -v

# --- Automation Logic ---

.PHONY: maint
maint: ## [App] Run remote maintenance (Update + DB Optimization)
	$(PYTHON) $(MAIN) --update --optimize

.PHONY: check
check: ## [App] Execute health diagnostics and generate Markdown report
	$(PYTHON) $(MAIN)

.PHONY: all
all: up check ## [Full] Lifecycle: Up -> Diagnose -> Prompted Cleanup
	@echo ""
	@read -p "Lifecycle complete. Run 'make clean' now? [y/N] " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		$(MAKE) clean; \
	else \
		echo "Cleanup skipped. Keeping infra active."; \
	fi

# --- Dependency Management (Modern uv) ---

.PHONY: setup
setup: ## [Deps] Bootstrap Python 3.14 environment and sync all libraries
	@echo "🚀 Initializing environment..."
	uv python install 3.14
	uv sync
	@echo "✅ Setup complete. Environment managed by uv."

.PHONY: lock
lock: ## [Deps] Regenerate the uv.lock file
	uv lock

# --- Build & Distribution ---

.PHONY: dist
dist: ## [Build] Compile into a standalone, path-aware binary
	@echo "📦 Compiling $(BINARY_NAME) with PyInstaller..."
	$(BUILD_CMD) $(BUILD_FLAGS) --name $(BINARY_NAME) $(MAIN)
	@echo "✅ Portable binary created: ./dist/$(BINARY_NAME)"

.PHONY: dist-clean
dist-clean: ## [Build] Remove build artifacts and specs
	rm -rf build/ dist/ *.spec

.PHONY: clean
clean: down dist-clean ## [Clean] Deep wipe: containers, logs, builds, and caches
	rm -rf logs/ .ruff_cache/ .pytest_cache/
	@echo "System fully sanitized."

# --- Help ---

.PHONY: help
help: ## [Utils] Display this help menu
	@echo "Maxx-WP-Automator CLI"
	@echo "---------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'
