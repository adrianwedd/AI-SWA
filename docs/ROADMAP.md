# Project Roadmap

This roadmap synthesizes the major milestones described in `ARCHITECTURE.md` and `VISION.md`.
Each phase builds on previous components and highlights key dependencies.

## Milestones
- **Bootstrap Core Loop** – Implement `Orchestrator`, `Planner`, `Executor`, `Reflector`, and `Memory` to run the self-improving loop.
- **CLI Interface** – Provide a command line wrapper that initializes the `Orchestrator`.
- **Persistence Layer** – Store tasks and state on disk through the `Memory` component.
- **Metrics & Self-Audit** – Integrate the `SelfAuditor` and `Reflector` to generate complexity metrics and propose refactors.
- **Task Broker & Workers** – Expose tasks via a FastAPI broker and execute them in containerized workers.
- **Node.js IOService** – Offload I/O-heavy functionality to a Node.js microservice communicating via gRPC.
- **Vision Engine** – Rank epics with Weighted Shortest Job First (WSJF) scores and a reinforcement-learning agent.
- **Plugin Ecosystem** – Allow community plugins with signed manifests and permission checks.
- **Ethical Sentinel** – Review new ideas and dependencies for security and ethics compliance.

## Timeline
| Phase | Target Date | Key Items | Dependencies |
|------|-------------|-----------|--------------|
| **1. Foundation** | Q1 2024 | Core loop, CLI, basic persistence | None |
| **2. Observability** | Q2 2024 | SelfAuditor, Reflector metrics | Foundation |
| **3. Distributed Execution** | Q3 2024 | Broker, Workers, Node.js IOService | Observability |
| **4. Intelligent Planning** | Q4 2024 | Vision Engine with RL agent | Distributed Execution |
| **5. Ecosystem & Governance** | Q1 2025 | Plugin marketplace, Ethical Sentinel | Intelligent Planning |

The timeline is intentionally high level. Each phase represents a checkpoint in the system's evolution where functionality from the previous phase is considered stable enough to support the next.
