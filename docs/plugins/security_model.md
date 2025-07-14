# Plugin Security Model

Plugins execute third-party code and therefore run inside a strict sandbox. Each
plugin directory contains a `manifest.json` describing required permissions. The
host validates this manifest against `plugins/manifest_schema.json` and applies a
policy file if configured via `PLUGIN_POLICY_FILE`.

The `plugins.executor.run_plugin()` helper copies plugin code into the sandbox
root, verifies the manifest and policy, then runs `plugin.py` with `python -I`
inside that directory using `ToolRunner`. Only the `python` command is allowed.
This prevents access to arbitrary binaries or paths outside the sandbox.

For environments with Docker installed, `plugins.executor.run_plugin_container()`
executes the plugin inside a minimal container built from
`plugins/sandbox/Dockerfile`. The container runs with `--network none` and a
read-only filesystem to further isolate third-party code.

If the policy file does not permit a plugin ID or its permissions, execution
fails before any code is run. When `PLUGIN_SIGNING_KEY` is set, manifests must
also include a valid signature.

## Execution Policies

Execution policies specify which plugins are allowed to run and what permissions they may request. The optional `plugins/policy.json` file maps plugin IDs to a list of permitted permissions as defined in `plugins/policy_schema.json`.

```json
{
  "plugins": {
    "techdebt": {"permissions": ["read_files"]},
    "example": {"permissions": ["read_files"]}
  }
}
```

When a policy file is configured via `PLUGIN_POLICY_FILE`, any plugin not listed or requesting additional permissions is rejected before execution.

## Sandbox Levels

Plugins run with one of two isolation levels:

1. **Default Sandbox** – Executes `plugin.py` with `python -I` using `ToolRunner`. Only the Python interpreter is available and the plugin directory is isolated from the rest of the repository.
2. **Container Sandbox** – When Docker is available, `run_plugin_container()` builds the sandbox image and runs the plugin with `--network none` and a read-only mount. Temporary write access is granted only at `/tmp`.

The container level provides stronger isolation and is used in CI and production environments.
