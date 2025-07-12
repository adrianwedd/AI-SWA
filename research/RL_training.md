# RL Training Data Generation

This guide describes how to produce state/action datasets for offline experiments.

1. Ensure the repository dependencies are installed.
2. Run the export script against a workload file:

```bash
python scripts/export_training_data.py data/rl_training/sample.jsonl --steps 500 --workload workload.json
```

Each line in the output JSONL file contains a normalized metrics state and the chosen action. Datasets are stored under `data/rl_training/`.
