# maxx-wp-automator

> A high-performance command-line diagnostic and automation engine designed for industrial-grade management of remote WordPress infrastructure via SSH. This project showcases advanced **Python systems programming**, and **Production-ready CI/CD orchestration**.

## Key Capabilities

* **Zero-Touch Provisioning:** Full-stack WordPress bootstrap (Core, Config, DB, and Admin) over secure SSH channels.
* **Idempotent Maintenance:** Intelligent remote database optimization and version parity updates for core/plugins.
* **Fail-Safe Disaster Recovery:** Automated pre-update snapshots via SFTP-tunneled database backups.
* **Observable Diagnostics:** Real-time logging and automated generation of structured Markdown health reports (`logs/wp_report.md`).
* **Single-Binary Distribution:** Compiled into a standalone, path-aware executable for zero-dependency portability.

---

## Tech Stack

* **Language:** **Python 3.14** (utilizing `NamedTuple`, `Protocol` structural typing, and `AsyncIO`)
* **Package Management:** **uv** (Standardized via `pyproject.toml` and deterministic `uv.lock`)
* **Infrastructure:** **Docker & Docker Compose** (Virtualized LAMP stack + MariaDB)
* **Orchestration:** **GNU Make** (Self-documenting task runner)
* **Security:** **Paramiko** (SSHv2 protocol) & **shlex** (Shell injection mitigation)

---

## Installation & Setup

### 1. Unified Environment Setup

This project uses **`uv`** to manage the entire toolchain. It will automatically download the required Python 3.14 interpreter and synchronize dependencies in seconds.

```bash
# Install the environment and sync dependencies
make setup

```

### 2. Infrastructure Bootstrapping

Orchestrate the local containerized environment and trigger the initial remote bootstrap:

```bash
make up

```

---

## Usage Guide

### Automated Workflows (Makefile Interface)

The `Makefile` serves as the primary control plane for the development lifecycle.

| Command | Action |
| --- | --- |
| `make setup` | **Modern Toolchain:** Installs Python 3.14 and syncs `uv.lock`. |
| `make up` | **Provision:** Spends up containers and executes initial `--setup`. |
| `make maint` | **Optimize:** Triggers remote updates and DB maintenance. |
| `make check` | **Audit:** Runs health checks and generates a diagnostic report. |
| `make dist` | **Compile:** Builds a portable, standalone binary in `./dist`. |
| `make clean` | **Reset:** Full wipe of containers, volumes, logs, and artifacts. |

### Standalone Binary Execution

The tool is designed for "run anywhere" capability. Once compiled, it operates without a local Python runtime.

```bash
./dist/maxx-wp --host 10.0.0.5 --user engineer --update

```

---

## Project Architecture

```text
.
├── .github/          # Automated CI/CD workflows
├── src/              # Core automation logic
├── pyproject.toml    # Universal project metadata (Industry Standard)
├── uv.lock           # Deterministic dependency locking
├── Makefile          # Unified task orchestration
├── main.py           # Application entry point
└── logs/             # (Auto-generated relative to binary)
    ├── wp_report.md  # Detailed diagnostic findings
    └── backups/      # Local database snapshots

```

---

## Security & Design Patterns

* **Deterministic State:** Uses `uv.lock` to ensure "it works on my machine" translates to "it works in production."
* **Binary-Safe Pathing:** Implements `sys.frozen` logic to ensure that even as a standalone executable, the tool correctly resolves relative paths for logs and backups.
* **Least Privilege:** Designed for non-root execution with strict ownership mapping between SSH and the web server.
* **Injection Guard:** All remote execution strings are sanitized using `shlex.quote()` to prevent command injection vulnerabilities.

---

> **Project Impact:** Developed to eliminate the friction of manual WordPress auditing. By abstracting complex SSH orchestration into a single, high-performance binary, this tool provides an enterprise-grade utility for maintaining remote server health with zero local overhead.
