# Contributing Guide

Thank you for helping improve **SelfArchitectAI**. Our workflow follows the [Liberal Contribution](GOVERNANCE.md) model.

## Development Setup

1. Install dependencies exactly as pinned:
   ```bash
   pip install -r requirements.txt
   ```
2. Install and enable pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Commit Guidelines
- Use the `type(scope): description` style described in `AGENTS.md`.
- Ensure a clean working tree before committing.
- Run the test suite:
  ```bash
  pytest --maxfail=1 --disable-warnings -q
  ```

Contributions are welcomed via pull requests. See [GOVERNANCE.md](GOVERNANCE.md) for how decisions are made.
