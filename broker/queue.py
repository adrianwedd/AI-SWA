import os
import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
QUEUE_NAME = os.getenv("TASK_QUEUE", "tasks")


def publish_task(task_id: int) -> None:
    """Publish task ID to RabbitMQ queue."""
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=str(task_id))
    connection.close()

