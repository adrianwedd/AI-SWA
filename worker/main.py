"""Command-line worker that processes tasks from the broker queue.

The worker contacts the broker specified by ``BROKER_URL`` and requests the
next available task via ``/tasks/next``. Each task may provide a shell
``command`` which is executed asynchronously. Results are posted back using
``/tasks/{id}/result``.
"""

import logging
import os
import asyncio
import requests
import sentry_sdk
from core.telemetry import setup_telemetry
from config import load_config
from core.log_utils import configure_logging
from core.async_runner import AsyncRunner

config = load_config()
BROKER_URL = config["worker"]["broker_url"]
CONCURRENCY = int(config["worker"].get("concurrency", 2))
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
setup_telemetry(
    service_name="worker",
    metrics_port=int(config["worker"]["metrics_port"]),
    jaeger_endpoint=config["tracing"]["jaeger_endpoint"],
)
configure_logging()
logger = logging.getLogger(__name__)


def fetch_next_task():
    """Return the next task from the broker or ``None`` if the queue is empty."""
    api_key = config["security"]["api_key"]
    headers = {"X-API-Key": api_key} if api_key else {}
    resp = requests.get(f"{BROKER_URL}/tasks/next", headers=headers)
    resp.raise_for_status()
    return resp.json()


async def process_task(runner: AsyncRunner, task: dict, sem: asyncio.Semaphore):
    command = task.get("command")
    if not command:
        return
    async with sem:
        result = await runner.run(command)
    logger.info("Executed command for task %s", task["id"])
    api_key = config["security"]["api_key"]
    headers = {"X-API-Key": api_key} if api_key else {}
    requests.post(
        f"{BROKER_URL}/tasks/{task['id']}/result",
        json={
            "stdout": result["stdout"],
            "stderr": result["stderr"],
            "exit_code": result["exit_code"],
        },
        headers=headers,
    ).raise_for_status()
    logger.info("Reported result for task %s", task["id"])


async def main_async():
    logger.info("Worker starting")
    runner = AsyncRunner()
    sem = asyncio.Semaphore(CONCURRENCY)
    pending = []
    while True:
        task = fetch_next_task()
        if not task:
            break
        pending.append(asyncio.create_task(process_task(runner, task, sem)))
    if pending:
        await asyncio.gather(*pending)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
