"""Command-line worker that polls the broker for pending tasks.

The script contacts the broker specified by ``BROKER_URL`` and retrieves any
pending tasks. Each task may provide a shell ``command`` which is executed in
an isolated subprocess. The worker then posts the command's ``stdout``,
``stderr`` and ``exit_code`` back to the broker.
"""

import logging
import asyncio
import requests
from core.telemetry import setup_telemetry
from core.config import load_config
from core.log_utils import configure_logging
from core.async_runner import AsyncRunner

config = load_config()
BROKER_URL = config["worker"]["broker_url"]
CONCURRENCY = int(config["worker"].get("concurrency", 2))
setup_telemetry(
    service_name="worker",
    metrics_port=int(config["worker"]["metrics_port"]),
)
configure_logging()
logger = logging.getLogger(__name__)


def fetch_tasks():
    api_key = config["security"]["api_key"]
    headers = {"X-API-Key": api_key} if api_key else {}
    resp = requests.get(f"{BROKER_URL}/tasks", headers=headers)
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
    tasks = fetch_tasks()
    runner = AsyncRunner()
    sem = asyncio.Semaphore(CONCURRENCY)
    await asyncio.gather(*(process_task(runner, t, sem) for t in tasks))


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
