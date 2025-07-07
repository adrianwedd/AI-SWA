# Governance

The Ethical Sentinel component enforces policy compliance for agent actions. When enabled, the orchestrator
loads a JSON policy file specifying blocked action IDs. If a task's ID matches an entry in `blocked_actions`,
the Sentinel prevents execution and logs a message.

This mechanism ensures that high‑risk tasks can be centrally disabled without modifying code. Policies are
loaded lazily when first evaluated so updates take effect on the next run.
