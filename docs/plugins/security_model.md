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
