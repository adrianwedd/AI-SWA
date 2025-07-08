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

## Packaging Plugins

Use `scripts/package_plugin.py` to bundle a plugin for distribution. Run:

```bash
python scripts/package_plugin.py plugins/example_plugin
```

The script creates `dist/<id>-<version>.zip` containing `manifest.json` and all
Python source files while excluding compiled artifacts.

## Signing Plugins

The CI pipeline installs [cosign](https://docs.sigstore.dev/cosign/overview/) and
signs each packaged plugin. The private key is provided via the `COSIGN_KEY`
secret, and the signature file (`.sig`) is uploaded alongside the plugin
archive. You can verify a signature locally using your public key:

```bash
cosign verify-blob --key cosign.pub dist/example-0.1.0.zip \
  --signature dist/example-0.1.0.zip.sig
```

## Policy Enforcement

Administrators may define `plugins/policy.json` to whitelist approved plugins.
The file follows `plugins/policy_schema.json` and maps each plugin ID to the
permissions it may use. When present, the plugin loader rejects any plugin not
listed or requesting permissions outside its allowed set. Use the
`PLUGIN_POLICY_FILE` environment variable to specify an alternate policy path.

## Sandbox Testing

All plugins are executed in a minimal Docker sandbox during CI. The sandbox image
is defined in [`plugins/sandbox/Dockerfile`](../../plugins/sandbox/Dockerfile)
and mounted read-only with no network access. See
[`sandbox.md`](sandbox.md) for details.
