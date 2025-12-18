# Contributing to maxx-wp-automator

First off, thank you for considering contributing to **maxx-wp-automator**! This project aims to maintain high standards for DevOps automation, and your help is vital.

## Development Setup

This project requires **Python 3.14**, **Docker**, and the **uv** package manager. We use a strictly isolated environment to ensure binary builds are consistent.

1. **Fork and Clone:**
```bash
git clone https://github.com/your-username/maxx-wp-automator.git
cd maxx-wp-automator

```


2. **Initialize the Environment:**
We use Conda for the interpreter and `uv` for lightning-fast dependency resolution.
```bash
conda env create -f environment.yml
conda activate wp-automator
make setup

```


3. **Spin Up Test Infrastructure:**
The included `Makefile` handles the Docker orchestration and WordPress bootstrapping automatically.
```bash
make up

```



---

## Contribution Guidelines

### 1. Development Standards

* **Static Analysis:** We use `ruff` for linting and formatting.
* **Type Safety:** We use `pyright` (or `basedpyright`) for type checking. Ensure your `Protocol` and `NamedTuple` implementations are correctly typed.
* **Binary Awareness:** Any feature involving file I/O must use the `get_base_path()` utility in `main.py` to ensure compatibility with PyInstaller's "frozen" state.

### 2. Pull Request (PR) Process

1. **Branching:** Create a feature branch (`feat/name`) or bugfix branch (`fix/name`).
2. **Local Validation:** Before submitting, ensure your code passes the following:
```bash
make check   # Validate app logic
make dist    # Ensure the project still compiles to a binary

```


3. **Commit Messages:** We follow **Conventional Commits** (e.g., `feat: add logging obfuscation`).
4. **Documentation:** Update the `README.md` if you add new CLI arguments or `Makefile` targets.

### 3. Reporting Issues

* Use **GitHub Issues** to report bugs or request features.
* For bugs, provide the output of `make help` to verify your environment setup and include your host OS details.

---

## Build System Architecture

When adding new libraries, do not just add them to `requirements.txt`. Follow this flow:

1. Add the dependency to `main.py`.
2. Run `make deps` to freeze the updated environment.
3. If the library uses C-extensions (like `paramiko`), update the `BUILD_FLAGS` in the `Makefile` to include the necessary `--collect-all` hooks.

## License

By contributing to this project, you agree that your contributions will be licensed under the **AGPLv3 License**.
