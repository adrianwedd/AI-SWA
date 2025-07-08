# Governance

The Ethical Sentinel component enforces policy compliance for agent actions. When enabled, the orchestrator
loads a JSON policy file specifying blocked action IDs. If a task's ID matches an entry in `blocked_actions`,
the Sentinel prevents execution and logs a message.

This mechanism ensures that high‑risk tasks can be centrally disabled without modifying code. Policies are
loaded lazily when first evaluated so updates take effect on the next run.

## Plugin Governance

Third-party plugins must pass a standardized certification process before publication. The CI workflow runs dependency audits, static analysis, secret scanning and sandboxed tests. Only plugins that pass all checks are signed with the marketplace key using `cosign`.

Administrators may restrict which plugins are allowed by providing `plugins/policy.json`. This file maps plugin IDs to approved permission sets. Any plugin not listed or requesting additional permissions is rejected at load time.

## Dependency Controls

Production dependencies are locked in `requirements.lock`. The pipeline runs `pip-audit` and Snyk to detect vulnerabilities. When issues are discovered, update the package versions and regenerate the lock file as described in [`docs/ci/dependency_updates.md`](ci/dependency_updates.md).
