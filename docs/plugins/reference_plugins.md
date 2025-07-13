# Reference Plugins

The plugin marketplace includes sample plugins used for testing and documentation purposes.
These reference plugins demonstrate how a manifest and `plugin.py` should be structured.

## Example Plugin

Located in [`plugins/example_plugin`](../../plugins/example_plugin), this minimal
plugin prints a short message when executed. It requires only the `read_files`
permission and has no external dependencies.

## Tech Debt Analyzer

[`plugins/tech_debt_analyzer`](../../plugins/tech_debt_analyzer) provides a small
utility that runs the built-in `SelfAuditor` against a target directory to
calculate code complexity metrics. It illustrates how plugins can leverage the
core modules while remaining sandboxed.

## Packaging and Uploading

Use `plugins/cli.py` to validate and package any plugin directory:

```bash
python plugins/cli.py validate plugins/tech_debt_analyzer
python plugins/cli.py package plugins/tech_debt_analyzer
```

The resulting archive in `dist/` can be signed and uploaded to the marketplace
with the `upload` command when a service endpoint is available.
