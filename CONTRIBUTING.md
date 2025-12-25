# Contributing to maxx-wp-automator

First off, thank you for considering contributing! We aim for **high-performance DevOps automation**, and your contributions help maintain the standard for others.

## Development Setup

This project uses **Python 3.14** and the **`uv`** package manager.

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/maxx-wp-automator.git
cd maxx-wp-automator

```

### 2. Initialize the Environment

`uv` will automatically manage your Python 3.14 installation and create a virtual environment in `.venv/`.

```bash
# This installs Python 3.14, creates the venv, and syncs all dependencies
make setup

```

### 3. Spin Up Test Infrastructure

We use Docker to simulate the remote WordPress environment locally.

```bash
make up

```

---

## Contribution Guidelines

### 1. Engineering Standards

* **Static Analysis:** We use **Ruff** for linting. Run `uv run ruff check .` before committing.
* **Strict Typing:** We use **basedpyright** for type checking. All new functions must have explicit type hints.
* **Binary Portability:** We use **PyInstaller**. Any file I/O must use the `get_base_path()` helper to resolve paths correctly when the app is "frozen" in a binary.

### 2. Pull Request (PR) Process

1. **Branching:** Use `feat/` for new features and `fix/` for bugfixes.
2. **Pre-Flight Checks:** Your PR must pass these local checks:
```bash
make check    # Logic validation
make dist     # Verify binary compilation still works

```


3. **Conventional Commits:** We use structured messages (e.g., `feat(auth): add ssh-key rotation`).

### 3. Adding Dependencies

**Do not edit `requirements.txt`.** This project uses `pyproject.toml`.

* To add a production library: `uv add <package>`
* To add a development tool: `uv add --dev <package>`
* To add a build-only tool: `uv add --group build <package>`

---

## License

By contributing, you agree that your code will be licensed under the **AGPLv3 License**.

---

### Pro-Tip for Contributors

If you use **VS Code**, `uv` creates a standard `.venv` folder. When you open the project, simply select the interpreter located at `./venv/bin/python` for full IntelliSense and Type-checking support.
