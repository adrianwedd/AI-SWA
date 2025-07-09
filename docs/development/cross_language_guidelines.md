# Cross-Language gRPC Service Guidelines

These conventions ensure Python, Rust and Node services interoperate smoothly. All synchronous service-to-service calls use gRPC with Protocol Buffers defined under [`proto/`](../../proto).

## Python Services

- Generate stubs using `python -m grpc_tools.protoc` with the same proto files used by other languages.
- Expose server implementations using `grpc.aio` or `grpc`.
- Clients should load connection settings from `config.yaml` and expose helper functions. See [`core/io_client.py`](../../core/io_client.py) for calling the Node service.

## Rust Services

- Include generated code via `tonic::include_proto!("aiswa")`.
- Implement gRPC servers with `tonic`. Example: [`services/rust_bridge`](../../services/rust_bridge) exposes a `Bridge` service returning reversed strings.
- Bind the service to `0.0.0.0` on the port configured in `config.yaml`.

## Node Services

- Use `@grpc/grpc-js` and `@grpc/proto-loader` to load the shared proto definitions.
- Export a metrics endpoint with Prometheus counters for each RPC method.
- The [`services/node`](../../services/node) directory provides a reference `IOService` implementation handling file operations.

## Shared Practices

1. **Single Source of Truth** – Proto files in `proto/` are canonical. Regenerate stubs whenever they change.
2. **Ports and Hosts** – All services read host/port from `config.yaml` to allow composition via Docker.
3. **Error Handling** – Map language-specific errors to appropriate gRPC status codes (`INVALID_ARGUMENT`, `INTERNAL`, etc.).
4. **Observability** – Collect request counts and latencies with OpenTelemetry or Prometheus metrics as shown in the Node example.

Following these guidelines keeps the system language-agnostic while enabling each service to leverage its ecosystem effectively.
