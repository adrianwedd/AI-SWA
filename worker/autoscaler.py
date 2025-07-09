"""Simple auto-scaler for worker processes."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from urllib.parse import urlparse

import requests

from config import load_config


class AutoScaler:
    """Spawn or terminate workers based on broker queue length."""

    def __init__(
        self,
        broker_url: str,
        metrics_port: int,
        max_workers: int = 4,
        interval: float = 1.0,
        loops: int | None = None,
    ) -> None:
        self.broker_url = broker_url.rstrip("/")
        self.metrics_port = metrics_port
        self.max_workers = max_workers
        self.interval = interval
        self.loops = loops
        self.workers: list[subprocess.Popen] = []

    # ------------------------------------------------------------------
    def _metrics_url(self) -> str:
        host = urlparse(self.broker_url).hostname or "localhost"
        return f"http://{host}:{self.metrics_port}/metrics"

    # ------------------------------------------------------------------
    def _queue_length(self) -> int:
        try:
            resp = requests.get(self._metrics_url(), timeout=1)
        except requests.RequestException:
            return 0
        for line in resp.text.splitlines():
            if line.startswith("broker_queue_length"):
                try:
                    return int(float(line.split()[-1]))
                except ValueError:
                    return 0
        return 0

    # ------------------------------------------------------------------
    def _spawn_worker(self) -> None:
        env = os.environ.copy()
        env.setdefault("BROKER_URL", self.broker_url)
        env.setdefault("WORKER_METRICS_PORT", "0")
        proc = subprocess.Popen(
            [sys.executable, "-m", "worker.main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )
        self.workers.append(proc)

    # ------------------------------------------------------------------
    def _stop_worker(self) -> None:
        proc = self.workers.pop()
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    # ------------------------------------------------------------------
    def step(self) -> None:
        desired = min(self.max_workers, self._queue_length())
        while len(self.workers) < desired:
            self._spawn_worker()
        while len(self.workers) > desired:
            self._stop_worker()

    # ------------------------------------------------------------------
    def run(self) -> None:
        count = 0
        while self.loops is None or count < self.loops:
            self.step()
            time.sleep(self.interval)
            count += 1
        while self.workers:
            self._stop_worker()


def main() -> None:
    cfg = load_config()
    broker_url = cfg["worker"]["broker_url"]
    metrics_port = int(cfg["broker"]["metrics_port"])
    max_workers = int(os.getenv("AUTOSCALER_MAX_WORKERS", "4"))
    interval = float(os.getenv("AUTOSCALER_INTERVAL", "1"))
    loops_env = os.getenv("AUTOSCALER_LOOPS")
    loops = int(loops_env) if loops_env is not None else None
    scaler = AutoScaler(
        broker_url=broker_url,
        metrics_port=metrics_port,
        max_workers=max_workers,
        interval=interval,
        loops=loops,
    )
    scaler.run()


if __name__ == "__main__":  # pragma: no cover - CLI
    main()

