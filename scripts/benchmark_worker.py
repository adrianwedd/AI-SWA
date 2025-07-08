import argparse
import subprocess
import time


def benchmark(num_tasks: int = 5, command: str = "echo hi") -> float:
    start = time.time()
    for _ in range(num_tasks):
        subprocess.run(command, shell=True, check=False, capture_output=True)
    duration = time.time() - start
    return num_tasks / duration


def main():
    parser = argparse.ArgumentParser(description="Benchmark worker throughput")
    parser.add_argument("--tasks", type=int, default=5)
    parser.add_argument("--command", default="echo hi")
    args = parser.parse_args()
    tps = benchmark(args.tasks, args.command)
    print(f"Baseline throughput: {tps:.2f} tasks/sec")


if __name__ == "__main__":
    main()

