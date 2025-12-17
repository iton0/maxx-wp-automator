# Contributing to maxx-wp-automator

First off, thank you for considering contributing to **maxx-wp-automator**! It’s people like you that make the open-source community such an amazing place to learn, inspire, and create.

## 🛠️ Development Setup

Since this project uses a specific **Python 3.14+** environment and **Docker**, please follow these steps to set up your local development environment:

1. **Fork the Repository** on GitHub.
2. **Clone your Fork:**
```bash
git clone https://github.com/your-username/maxx-wp-automator.git
cd maxx-wp-automator

```


3. **Set up the Environment:**
We use Conda and `uv` to manage dependencies.
```bash
conda env create -f environment.yml
conda activate wp-automator
uv pip install -r requirements.txt

```


4. **Launch the Test Infrastructure:**
```bash
docker compose up -d --build

```



## 📜 Contribution Guidelines

### 1. Reporting Bugs

* Use the **GitHub Issues** tab.
* Describe the bug and provide steps to reproduce it.
* Include your OS version and the output of `python --version`.

### 2. Suggesting Enhancements

* Open a **GitHub Issue** and describe the feature you'd like to see.
* Explain why this feature would be useful to other users.

### 3. Pull Requests (PRs)

* **Branch Naming:** Use descriptive names like `fix/connection-timeout` or `feat/slack-notifications`.
* **Code Style:** We use `ruff` for linting. Please run `ruff check .` before submitting.
* **Documentation:** If you add a new flag or feature, please update the `README.md`.
* **Commit Messages:** Follow conventional commits (e.g., `feat: add multisite support`).

## ⚖️ License

By contributing to this project, you agree that your contributions will be licensed under the **AGPLv3 License**.
