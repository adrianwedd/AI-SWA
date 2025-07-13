# Plugin Marketplace Service API

The plugin marketplace hosts vetted plugin archives and exposes both gRPC and REST interfaces. Services and users may retrieve plugins or publish new versions through these endpoints.

## gRPC Interface

The `PluginMarketplace` service defined in [`proto/plugin_marketplace.proto`](../../proto/plugin_marketplace.proto) provides four RPC methods:

```
service PluginMarketplace {
  rpc ListPlugins(Empty) returns (PluginList);
  rpc DownloadPlugin(PluginRequest) returns (PluginData);
  rpc SubmitReview(SubmitReviewRequest) returns (Empty);
  rpc ListReviews(ReviewRequest) returns (ReviewList);
}
```

* **ListPlugins** – returns basic metadata for all available plugins.
* **DownloadPlugin** – fetches a zipped plugin archive by ID.
* **SubmitReview** – records a 1–5 rating and comment for a plugin.
* **ListReviews** – retrieves stored reviews for a plugin.

## REST Endpoints

`service.py` exposes a matching REST API for lightweight clients:

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/plugins` | List all plugins |
| `GET` | `/plugins/{id}/download` | Download a plugin archive |
| `PUT` | `/plugins/{id}` | Create or update plugin metadata and file path |
| `DELETE` | `/plugins/{id}` | Remove a plugin from the marketplace |
| `POST` | `/plugins/{id}/reviews` | Submit a review |
| `GET` | `/plugins/{id}/reviews` | Retrieve reviews |

A GraphQL schema mirroring these endpoints is documented in [`docs/api/plugin_marketplace_graphql.md`](../api/plugin_marketplace_graphql.md).

## Security Boundaries

Plugins are distributed as signed zip archives. The marketplace itself does not execute plugin code but stores the archives in a dedicated directory. Security protections are enforced when plugins are run by the orchestrator:

1. **Manifest Validation** – each plugin must include a `manifest.json` describing its ID, version and requested permissions. The manifest is validated against [`plugins/manifest_schema.json`](../../plugins/manifest_schema.json) and checked against any policy file.
2. **Signature Verification** – when `PLUGIN_SIGNING_KEY` is configured, plugin manifests must include a valid HMAC signature. Unsigned or tampered plugins are rejected.
3. **Sandbox Execution** – plugins run inside the Docker sandbox described in [`sandbox.md`](sandbox.md). The container disables network access and mounts the repository read‑only to prevent side effects.

These boundaries ensure that plugins retrieved via the REST or gRPC APIs cannot compromise the host when later executed.
