# Using the VS Code Dev Container

The repository ships a ready to use [Dev Container](https://code.visualstudio.com/docs/devcontainers/containers) definition.
It provides a consistent environment with Python 3.12 and the required extensions installed.

This container is especially useful when Docker is not available for running the
full `docker-compose` workflow. Opening the repository in the Dev Container lets
you install dependencies and run tests without needing a local Docker daemon.

## Quick start

1. Install the **Dev Containers** extension for VS Code.
2. Open this folder in VS Code and choose **Reopen in Container** when prompted.
3. The image `mcr.microsoft.com/devcontainers/python:3.12` will be pulled and dependencies installed using `pip install -r requirements.txt`.

## Running tests

A `Run Tests` task is included in the container. Trigger it from the command palette (`Run Task`) or execute:

```bash
pytest --maxfail=1 --disable-warnings -q
```

This runs the suite inside the container using the same configuration as CI.
