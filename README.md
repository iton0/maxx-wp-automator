# maxx-wp-automator

> A high-performance command-line diagnostic and automation tool designed to manage remote WordPress installations via SSH. This project demonstrates proficiency in **Python automation**, **Linux systems administration**, **Docker orchestration**, and **modern package management**.

## Features

* **Zero-Touch Bootstrap:** Automated WordPress installation (Core, Config, DB, and Admin) via SSH.
* **Environment Reset:** A "Clean" function to safely wipe remote files and reset the database.
* **Automated Maintenance:** Remote database optimization and core/plugin updates in a single command.
* **Disaster Recovery:** Automated database backups transferred locally via SFTP before updates.
* **Professional Reporting:** Generates a structured Markdown report (`logs/wp_report.md`) after every run.
* **Portable Distribution:** Can be compiled into a standalone, path-aware binary for zero-dependency execution.

---

## Tech Stack

* **Python 3.14+** (Utilizing `NamedTuple`, `Protocol` typing, and `Paramiko`)
* **Package Management:** **Conda** (Isolation) + **uv** (High-speed resolution)
* **Infrastructure:** **Docker & Docker Compose** (LAMP stack + MariaDB)
* **Orchestration:** **GNU Make** (Self-documenting build system)
* **CMS Tooling:** **WP-CLI**

---

## Installation & Setup

### 1. Initialize the Python Environment

This project uses **Conda** for the runtime and **uv** for library synchronization.

```bash
# Create and activate the environment
conda env create -f environment.yml
conda activate wp-automator

# Sync dependencies using the optimized uv manager
make setup

```

### 2. Infrastructure Setup

The provided **Makefile** automates the Docker builds and initial WordPress bootstrap:

```bash
make up

```

---

## Usage Guide

### Workflow Automation (via Make)

The `Makefile` serves as the primary entry point. Run `make` or `make help` to see all available commands.

| Command | Action |
| --- | --- |
| `make up` | Builds containers, waits for SSH, and performs a fresh `--setup`. |
| `make maint` | Triggers `--update` (with backup) and `--optimize`. |
| `make check` | Runs a standard health check and generates the Markdown report. |
| `make dist` | Compiles the project into a standalone binary in `./dist`. |
| `make clean` | Full teardown: removes containers, logs, and build artifacts. |

### Standalone Binary Execution

Once built via `make dist`, the tool can be run as a single executable without a Python environment. It is fully path-aware and will create its own `logs/` directory in its current location.

```bash
./dist/maxx-wp --host 1.2.3.4 --user deploy --update

```

---

## Project Structure

* **`main.py`**: Core automation logic with binary-safe path resolution.
* **`Makefile`**: Orchestration logic for Docker, dependencies, and PyInstaller.
* **`environment.yml`**: Streamlined Conda environment manifest.
* **`logs/`**: (Auto-generated relative to execution point)
    * `wp_report.md`: Detailed diagnostic findings.
    * `wp_backup_[timestamp].sql`: Local database snapshots.
    * `maintenance_[date].log`: Technical execution logs.



---

## Security & Architecture

* **Binary-Safe Pathing:** Uses `sys.frozen` detection to ensure file I/O (logs/backups) is always relative to the executable path, preventing data loss in temporary directories.
* **Non-Root Execution:** Operations are performed as `testuser` with consistent ownership between SSH and the web server.
* **Command Sanitization:** All remote commands are wrapped in `shlex.quote()` to prevent shell injection.
* **Idempotency:** The `--setup` routine verifies existing configurations to prevent accidental overwrites.

---

### Project Impact

> Developed as a DevOps utility to eliminate manual WordPress audit tasks. By orchestrating SSH connections with WP-CLI and bundling the logic into a portable binary, this tool ensures that remote environments remain secure, updated, and optimized with zero manual intervention or local dependency overhead.
