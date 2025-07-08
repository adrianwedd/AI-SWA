# Worker Throughput Baseline

The sequential worker processed 5 trivial tasks using the `scripts/benchmark_worker.py` script.

```
$ python scripts/benchmark_worker.py --tasks 5 --command "echo hi"
Baseline throughput: 5.00 tasks/sec
```

This baseline is used to compare against the new asynchronous implementation.
