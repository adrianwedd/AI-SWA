# Cross-Language Guidelines

This document summarizes how AI-SWA combines Python with Rust and Node.js as outlined in [RB-004](../../research/RB-004_Cross_Language_Design.md). The aim is to keep each component in the language best suited for its workload while maintaining clear boundaries.

## Component Boundaries

- **Python** – Primary language for the Orchestrator, Planner, Worker and plugin governance. Chosen for rapid iteration and scripting flexibility.
- **Rust** – Used for CPU-bound performance hotspots. Services like `rust_bridge` and future extensions built with PyO3 accelerate heavy analysis routines.
- **Node.js** – Runs I/O-heavy tasks. The `IOService` and future real-time dashboards operate as separate Node services communicating via gRPC.

These boundaries follow the phased roadmap described in the Polyglot Microservices Strategy.

## FFI Type-Safety Guidelines

1. Expose Rust functions through `PyO3` with explicit types and `PyResult` error handling.
2. Avoid `unsafe` blocks in shared modules. If unavoidable, cover them with Python-side tests.
3. Validate all data crossing language boundaries and convert to concrete structs instead of using raw pointers.
4. Integrate Node.js via gRPC rather than in-process bindings to maintain isolation and type safety.
5. Regenerate gRPC stubs from `.proto` definitions whenever they change to keep bindings consistent.

## Multi-Language CI Strategy

- Execute `pytest` for Python, `cargo test` for Rust and `npm test` with `npm audit` for Node services.
- Apply shared GitHub Actions templates so every service performs dependency scanning (pip-audit, cargo-audit, npm audit).
- Build Docker images for each service and run integration tests starting the Python core plus all foreign services.
- The workflow fails if any language's tests or security checks do not pass.

Following these practices ensures the small set of languages remains manageable while providing the performance and concurrency benefits explored in RB-004.
