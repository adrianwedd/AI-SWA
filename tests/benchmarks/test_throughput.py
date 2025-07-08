import asyncio
import time
from core.async_runner import AsyncRunner

async def run_benchmark(num_tasks: int = 5) -> float:
    runner = AsyncRunner()
    cmd = ["python", "-c", "import time; time.sleep(0.1)"]
    start = time.perf_counter()
    await asyncio.gather(*(runner.run(cmd) for _ in range(num_tasks)))
    duration = time.perf_counter() - start
    return num_tasks / duration

def test_async_runner_throughput():
    tps = asyncio.run(run_benchmark())
    assert tps > 10, f"throughput too low: {tps:.2f} tps"
