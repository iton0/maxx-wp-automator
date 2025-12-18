# Variables
PYTHON = python
MAIN   = main.py

.PHONY: up down maint check clean all

# 1. Spin up infrastructure and bootstrap WordPress
up:
	docker compose up -d --build
	@echo "Waiting for SSH to initialize..."
	@sleep 5
	$(PYTHON) $(MAIN) --clean --setup

# 2. Perform maintenance
maint:
	$(PYTHON) $(MAIN) --update --optimize

# 3. Quick Health Check
check:
	$(PYTHON) $(MAIN)

# 4. Stop and remove containers/volumes
down:
	docker compose down -v

# 5. Full wipe
clean: down
	rm -rf logs/
	@echo "All containers and local logs have been removed."

# 6. Full Lifecycle with Interactive Cleanup
all: up check
	@echo ""
	@read -p "Lifecycle complete. Do you want to run 'make clean' now? [y/N] " ans; \
	if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
		$(MAKE) clean; \
	else \
		echo "Cleanup skipped. Stopping running containers."; \
		$(MAKE) down; \
	fi
