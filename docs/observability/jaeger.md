# Jaeger Tracing

The observability stack now includes a Jaeger instance for viewing distributed traces. The service is defined in `docker-compose.yml` and listens on `http://localhost:16686`.

## Usage

1. Run `observability/generate_certs.sh` once to create certificates.
2. Start the stack with `docker-compose up`.
3. Execute your workflows as normal. Spans from each service are exported to Jaeger.
4. Open <http://localhost:16686> in your browser to explore traces.

All services send metrics to the OpenTelemetry Collector and traces directly to Jaeger using the `JAEGER_ENDPOINT` environment variable.
