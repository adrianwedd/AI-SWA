# Agent Release Comparison Scenarios

This document outlines consistent tests for evaluating one agent release against another.

## 1. Throughput Benchmarks

Run `scripts/benchmark_worker.py` with the same number of tasks across releases:

```bash
python scripts/benchmark_worker.py --tasks 5 --command "echo hi"
```

Record the `tasks/sec` value. Higher throughput indicates a faster worker implementation.

A second benchmark uses the asynchronous runner:

```bash
pytest tests/benchmarks/test_throughput.py -q
```

The test asserts minimum throughput but printing the result provides a direct comparison between releases.

## 2. Git History Scenarios

Adapt the [GitGoodBench](../research/Architectures%20for%20Continual%20Self-Improvement%20in%20AI-Driven%20Software%20Engineering.md) approach. Mine historical commits for

- bug fixes
- refactorings
- feature additions

Replaying these changes against the older release and the new release yields success/failure metrics and patch quality scores. Complex scenarios can be evaluated by prompting an LLM to judge commit clarity and coherence.

## 3. Key Metrics

For each scenario capture:

- **Tasks per second** – average throughput measured by the benchmarks.
- **Test pass rate** – percentage of benchmark scenarios where all unit tests succeed.
- **Code quality deltas** – lint and complexity score changes between releases.

These repeatable scenarios establish a baseline for comparing new agent versions and confirm improvements before deployment.
