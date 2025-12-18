# maxx-wp-automator

> A high-performance command-line diagnostic and automation tool designed to manage remote WordPress installations via SSH. This project demonstrates proficiency in **Python automation**, **Linux systems administration**, **Docker orchestration**, and **modern package management**.

## Features

* **Zero-Touch Bootstrap:** Automated WordPress installation (Core, Config, DB, and Admin) via SSH.
* **Environment Reset:** A "Clean" function to safely wipe remote files and reset the database.
* **Automated Maintenance:** Remote database optimization and core/plugin updates in a single command.
* **Disaster Recovery:** Automated database backups transferred locally via SFTP before updates.
* **Professional Reporting:** Generates a structured Markdown report (`logs/wp_report.md`) after every run.
* **Orchestrated Workflow:** Full lifecycle management from container spin-up to environment teardown via `make`.

---

## Tech Stack

* **Python 3.14+** (Utilizing `NamedTuple`, `Protocol` typing, and `Paramiko`)
* **Package Management:** **Conda** (Isolation) + **uv** (High-speed resolution)
* **Infrastructure:** **Docker & Docker Compose** (LAMP stack + MariaDB)
* **Orchestration:** **GNU Make**
* **CMS Tooling:** **WP-CLI**

---

## Installation & Setup

### 1. Initialize the Python Environment

This project uses **Conda** for the runtime and **uv** for library synchronization.

```bash
# Create and activate the environment
conda env create -f environment.yml
conda activate wp-automator

# Sync dependencies
uv pip install -r requirements.txt

```

### 2. Infrastructure Setup

The provided **Makefile** automates the Docker builds and initial WordPress bootstrap:

```bash
make up

```

---

## Usage Guide

### Workflow Automation (via Make)

The `Makefile` provides a high-level interface for all common tasks.

| Command | Action |
| --- | --- |
| `make up` | Builds containers, waits for SSH, and performs a fresh `--clean --setup`. |
| `make maint` | Triggers `--update` (with backup) and `--optimize`. |
| `make check` | Runs a standard health check and generates the Markdown report. |
| `make down` | Stops containers and removes Docker volumes. |
| `make clean` | Full teardown: runs `make down` and deletes local `logs/` directory. |
| `make all` | Executes a full lifecycle: Up → Check → Interactive Cleanup. |

### Manual Execution (via Python CLI)

For granular control or targeting external servers, use the Python CLI directly:

```bash
# Target a specific external host
python main.py --host 1.2.3.4 --user deploy --passw secret123 --update

# Perform only a database optimization
python main.py --optimize

```

---

## Project Structure

* **`main.py`**: The core automation logic using Paramiko and WP-CLI.
* **`Makefile`**: Short-hand aliases for infrastructure and script execution.
* **`logs/`**:
* `wp_report.md`: Detailed diagnostic findings.
* `wp_backup_[timestamp].sql`: Database snapshots pulled via SFTP.
* `maintenance_[date].log`: Technical execution logs.



---

## Security & Architecture

* **Non-Root Execution:** The tool connects as `testuser`. The Docker environment utilizes consistent ownership between the SSH user and the Apache web server.
* **Command Sanitization:** All remote commands are wrapped in `shlex.quote()` to prevent shell injection.
* **Idempotency:** The `--setup` routine verifies existing `wp-config.php` files to prevent accidental data overwrites on active sites.
* **Local-Remote Synergy:** By combining `paramiko.SSHClient` for commands and `SFTPClient` for backups, the tool ensures data is never left solely on the remote server during risky updates.

---

### Project Impact

> Developed as a DevOps utility to eliminate manual WordPress audit tasks. By orchestrating SSH connections with WP-CLI, this tool ensures that remote environments remain secure, updated, and optimized with zero manual intervention.
