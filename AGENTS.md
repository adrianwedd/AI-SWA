# AGENTS.md

## 1. Overview

This document serves as the official registry and specification for all autonomous agents operating within this repository. Its purpose is to define the roles, responsibilities, communication protocols, and operational boundaries of each agent to ensure a cohesive and conflict-free multi-agent system. This file is the ground truth for agent identity and capability.

---

## 2. Core Principles of Agency

All agents registered in this document adhere to the following principles:

* **Specialization:** Each agent has a single, well-defined responsibility (e.g., architecture, testing, documentation). This prevents overlapping concerns and promotes modularity.
* **Protocol-Driven:** Agents operate based on documented protocols (like the **Iterative Development Protocol**). Their behavior should be predictable and deterministic.
* **Asynchronous Communication:** Agents do not communicate directly. They interact asynchronously by modifying the state of the repository in a structured manner (e.g., updating `tasks.yml`, committing code, creating reports). Git serves as the universal message bus.
* **State Awareness:** Agents are responsible for ingesting the current state of the repository (`ARCHITECTURE.md`, `tasks.yml`, file structure) before taking action.

---

## 3. Agent Registry

This table provides a high-level summary of all active and proposed agents in the system.

| Agent ID         | Name / Role          | Responsibilities                                                                                                 | Primary Input(s)                                   | Primary Output(s)                                                                    | Status      |
| ---------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------ | ----------- |
| **SWA-CORE-01** | **Core Architect** | - Implements core functionality based on `tasks.yml`.<br>- Refines `ARCHITECTURE.md`.<br>- Decomposes epics into sub-tasks. | `tasks.yml`, `ARCHITECTURE.md`                     | New/modified Python code, unit tests, updated `tasks.yml`, updated `ARCHITECTURE.md` | **Active** |
| **SWA-QA-01** | **QA & Security Agent** | - Performs deep static analysis and security scanning.<br>- Runs integration tests.<br>- Generates bug reports as new tasks. | `feat(...)` and `fix(...)` commits, test suite results | New tasks in `tasks.yml` with the `bug` label, security vulnerability reports.      | Proposed    |
| **SWA-DOCS-01** | **Documentation Agent** | - Ensures code comments and docstrings are consistent.<br>- Audits `ARCHITECTURE.md` against implemented code.<br>- Auto-generates changelogs. | `docs(...)` commits, source code comments              | Pull requests with documentation improvements, `CHANGELOG.md`.                       | Proposed    |
| **SWA-SUPER-01** | **Supervisor Agent** | - Oversees the development lifecycle.<br>- Prioritizes epics.<br>- Activates specialized agents based on task labels.     | `git log`, `tasks.yml`                             | Modifications to task priorities and statuses in `tasks.yml`.                        | Proposed    |

---

## 4. Detailed Agent Specifications

### 4.1. SWA-CORE-01: Core Architect

* **Description:** The primary "builder" agent. SWA-CORE-01 is responsible for the main development loop of planning, documenting, building, testing, and committing new features as defined in the task list.
* **Operating Protocol:** Follows the **Iterative Development Protocol (IDP)**.
* **Activation:** Activated by the presence of `pending` tasks in `tasks.yml` with the `core` or `feat` label.
* **Communication Contract:**
    * **Reads:** Consumes tasks from `tasks.yml`. Reads architectural plans from `ARCHITECTURE.md`.
    * **Writes:** Produces Python source code in `core/` and tests in `tests/`. Updates `tasks.yml` by decomposing epics and marking work as `done`. Updates `ARCHITECTURE.md` with design refinements. All writes are committed to git following repository conventions.

---

## 5. Multi-Agent Interaction Protocol

As new agents become active, they must adhere to the following interaction model to prevent race conditions and conflicts:

1.  **Task-Based Activation:** An agent should only activate when a task with a relevant label (e.g., `test`, `docs`) is at the top of the priority queue.
2.  **Resource Locking (Conceptual):** Before beginning work, an agent should change the status of its target task in `tasks.yml` to `in_progress` and commit this change immediately. This signals to other agents that the task and its related artifacts are "locked."
3.  **Pull Request Workflow (for non-Core Agents):** To ensure stability, specialized agents like `SWA-QA-01` or `SWA-DOCS-01` should not commit directly to the `main` branch. Instead, they should create a feature branch, perform their work, and open a pull request. The `SWA-CORE-01` agent would then be responsible for reviewing and merging the pull request.

---

## 6. Protocol for Onboarding a New Agent

To introduce a new agent to the system, the following process must be followed:

1.  **Propose a Specification:** Open a pull request that adds or updates an entry for the new agent in this `AGENTS.md` file. The specification must include the agent's ID, responsibilities, and its full communication contract.
2.  **Develop the Agent:** Implement the agent's core logic, ensuring it adheres to the principles outlined in this document.
3.  **Update the Supervisor:** The logic of the `SWA-SUPER-01` agent (or the current primary agent) must be updated to recognize and delegate tasks to the new agent based on its specified activation triggers.
4.  **Merge and Activate:** Once the pull request is approved and merged, the new agent is considered a recognized part of the system.


---

## 7. Repository Workflow

- Follow the Iterative Development Protocol described in `README.md`.
- Keep `tasks.yml` up to date, marking tasks as `done` once implemented.
- Periodically run `python scripts/archive_tasks.py` to move completed tasks to
  `tasks_archive.yml`.

### Commit Messages

# Repository Guidelines for Codex Agent

These instructions apply to all files in this repository.

## Workflow
- Follow the Iterative Development Protocol described in `README.md`.
- Keep `tasks.yml` up to date, marking tasks as `done` once implemented.

## Commit Messages
- Use descriptive commit messages.
- For planning updates use `docs(planning): ...`.
- For features use `feat(component): ...`.
- For task completion use `chore(tasks): ...`.

### Testing

## Testing
- Run `pytest --maxfail=1 --disable-warnings -q` before every commit.
- Ensure a clean working tree (`git status`) before committing.

