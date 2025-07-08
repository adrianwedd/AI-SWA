# Task Queue Technology Evaluation

Two common options for implementing a lightweight queue are RabbitMQ and Redis. Both provide reliable message delivery but have different operational trade-offs.

## RabbitMQ
- Mature broker implementing the AMQP protocol.
- Supports complex routing, priorities and message acknowledgements.
- Requires separate service and management overhead.

## Redis
- In-memory data store with simple list commands (`BLPOP`, `BRPOP`).
- Easy to deploy and already widely used in many environments.
- Limited routing features and persistence is optional.

For the initial worker queue a full broker is unnecessary. SQLite already stores tasks and supports transactional updates. Therefore the prototype uses a simple `SELECT ... UPDATE` wrapped in a transaction to pop the next pending task. Redis remains a future option if scalability demands it.
