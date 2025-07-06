# Plugin Permissions Model

Plugins must declare a manifest file named `manifest.json` that specifies the plugin
metadata and requested permissions. Each manifest includes:

- `id`, `name`, and `version` fields.
- `permissions`: a list of capabilities the plugin requires (e.g. `read_files`, `network`).
- Optional `signature`: an HMAC-SHA256 signature of the manifest contents.

The host validates that all requested permissions are allowed and, when a signing
key is configured via the `PLUGIN_SIGNING_KEY` environment variable, verifies the
signature. Plugins lacking a valid signature are rejected when signing is
enabled.
