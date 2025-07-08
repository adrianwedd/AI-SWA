# Research Brief RB-004: Cross-Language Design

This outline explores approaches for mixing programming languages across the system while maintaining maintainability.

## Literature Summary
- **Polyglot microservices** leverage language-specific strengths; Martin Fowler notes benefits of autonomy and scalability.
- **FFI and gRPC** allow safe bindings between Rust, Python, and Node.js with minimal overhead.
- **Message queue protocols** such as NATS or Kafka decouple services for asynchronous coordination.

## Open Questions
- Which components benefit most from Rust's performance versus Python's flexibility?
- How can we enforce type safety across language boundaries?
- What tooling is required to manage multi-language builds in CI?

## Implementation Acceptance Criteria
- Adopt a microservice or plugin interface allowing Rust/Node services to integrate via gRPC or queues.
- Provide build scripts that compile foreign code and run tests in CI.
- Demonstrate one cross-language module exchanging data with the existing Python core.
