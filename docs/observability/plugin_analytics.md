# Plugin Marketplace Analytics

The plugin marketplace exposes basic Prometheus metrics for usage analytics. Metrics are defined in `services/plugin_marketplace/analytics.py` and collected by the OpenTelemetry Prometheus exporter.

## Metrics

- `plugin_downloads_total` — total number of plugin downloads
- `plugin_ratings_total` — count of submitted ratings
- `plugin_search_queries_total` — number of search queries executed

## Usage

1. Start the marketplace service with `METRICS_PORT` set to a non-zero port.
2. Visit `http://localhost:<port>/metrics` to view the raw metrics.
3. Import `grafana/dashboards/plugin_analytics.json` into Grafana to visualize the counters.
