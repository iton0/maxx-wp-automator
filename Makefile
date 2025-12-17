# Variables
USER = testuser
PASS = password
PORT = 2222
PYTHON = python
MAIN = main.py

.PHONY: up down clean test report

# 1. Spin up infrastructure and bootstrap WordPress
up:
	docker compose up -d --build
	@echo "Waiting for SSH to initialize..."
	@sleep 5
	$(PYTHON) $(MAIN) --user $(USER) --passw $(PASS) --port $(PORT) --clean --setup

# 2. Perform maintenance (Backup + Update + Optimize)
maint:
	$(PYTHON) $(MAIN) --user $(USER) --passw $(PASS) --port $(PORT) --update --optimize

# 3. Quick Health Check (Just Generate Report)
check:
	$(PYTHON) $(MAIN) --user $(USER) --passw $(PASS) --port $(PORT)

# 4. Tear down everything (Containers, Volumes, and Local Logs)
down:
	docker compose down -v
	rm -rf logs/

# 5. Full Lifecycle (Up, Check, then Down)
all: up check down
