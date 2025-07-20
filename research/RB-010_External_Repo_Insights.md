# Research Brief RB-010: External AI CLI Architectures

This brief documents insights gathered from inspecting two open-source projects: [Gemini CLI](https://github.com/google-gemini/gemini-cli) and [OpenAI Codex](https://github.com/openai/codex). Both provide command-line agents that interface with language models. Their designs help inform potential features for the AI-SWA project.

## Gemini CLI
- **Stack:** TypeScript/Node.js monorepo using `pnpm` with packages `cli`, `core`, and `vscode-ide-companion`.
- **CLI package:** Handles user input, manages display themes, and maintains history. Configurable via a rich set of command flags.
- **Core package:** Orchestrates API calls to Gemini, constructs prompts, and executes tools. Tools live under `packages/core/src/tools/` and include file system and shell helpers.
- **Interaction flow:** User input flows from the CLI to the core package. The core may call tools (after user confirmation for write operations) and then forwards results back to the CLI for display. The architecture document emphasises modularity and extensibility of tools.

## OpenAI Codex
- **Stack:** Primarily Rust (`codex-rs`) with a legacy TypeScript CLI. The Rust implementation aims for a zero-dependency install.
- **AGENTS.md:** Notes that code executes in a sandbox, disallowing network access via a `CODEX_SANDBOX_NETWORK_DISABLED` env variable. Contributors must run `just fmt` and `just fix` before PRs and run `cargo test --all-features`.
- **Codex Core:** Provides a protocol-driven engine documented in `codex-rs/core` with a newline-delimited JSON protocol for UIs. Concepts include `Session`, `Task`, and `Turn`. The protocol allows sending user input, streaming model responses, executing commands, and applying patches while waiting for user approvals when needed.
- **CLI packages:** There is a Rust CLI crate invoking the core protocol and a deprecated TypeScript implementation. Configuration is stored in `config.toml` under `$CODEX_HOME` and can also be set via command-line flags.

## Implementation Ideas for AI-SWA
- **CLI Frontend + Core Backend:** Following Gemini CLI’s separation, AI-SWA could expose a simple CLI package that forwards requests to existing orchestration services, keeping user experience decoupled from backend logic.
- **Extensible Tool System:** Both projects use a plugin or tool mechanism for environment actions. A similar registry of safe tools would allow users to add file, shell, or network operations with explicit approval steps.
- **Protocol for Sessions and Tasks:** Codex defines a structured protocol with `Session`, `Task`, and `Turn`, which could inspire a formal message bus for AI-SWA agents and plugins.
- **Sandbox Controls:** Leveraging Codex’s environment variable approach, AI-SWA could enforce offline/sandbox modes during unit tests or when running in restricted environments.

These patterns demonstrate production-ready approaches to building CLI-driven agents and can guide future enhancements in the AI-SWA architecture.
