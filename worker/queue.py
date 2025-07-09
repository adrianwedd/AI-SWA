import os
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("TASK_QUEUE", "tasks")


def consume(callback):
    """Consume one message from RabbitMQ and pass payload to callback."""
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    method_frame, _, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=True)
    if method_frame:
        callback(body.decode())
    connection.close()

