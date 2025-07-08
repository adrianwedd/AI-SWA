# Plugin API and Isolation

Plugins extend AI-SWA with optional features. Each plugin resides in its own directory under `plugins/` with at least two files:

- `manifest.json` – metadata validated against `plugins/manifest_schema.json`
- `plugin.py` – module containing a `run(**kwargs)` entry point

The orchestrator imports `<plugin>/plugin.py` and calls `run()` inside a sandboxed Docker container. The sandbox defined in [`plugins/sandbox/Dockerfile`](../../plugins/sandbox/Dockerfile) runs without network access or write permissions outside `/tmp`.

## Entry Point Requirements

```python
# plugins/my_plugin/plugin.py

def run(**kwargs) -> None:
    """Execute plugin logic."""
    ...
```

- `run` must be idempotent and side effect free beyond its output.
- Arguments are passed as keyword parameters defined by the orchestrator.

## Isolation Model

1. Plugins execute inside the sandbox image during CI and before marketplace publication.
2. The container uses a non‑root user and mounts the repository read‑only.
3. Network access is disabled unless the `network` permission is granted.

This model prevents malicious plugins from modifying the host system or contacting external services during certification.

## Threat Analysis

All manifests are validated and permissions checked before execution. When `PLUGIN_SIGNING_KEY` is configured, each manifest must include a valid HMAC signature. Policy files may further restrict which plugins and permissions are allowed. Combined with static analysis and sandbox testing, these steps mitigate supply chain risks.
