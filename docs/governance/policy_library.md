# Policy Library Guidelines

The `policies/` directory stores JSON files that define what actions agents are prohibited from executing. Each policy must conform to `policy_schema.json`.

## Authoring Policies

1. Create a new `.json` file under `policies/` or a nested folder such as `policies/examples/`.
2. Include a `blocked_actions` array listing task or action IDs to disable.
3. Validate the file against `policies/policy_schema.json` using `jsonschema` before committing.
4. Keep names short and descriptive so administrators can easily enable or disable them.

Policies placed in a directory are merged together at runtime by the `EthicalSentinel`. This allows a library of reusable policy modules. Remove actions from the list to re-enable them on the next run.
