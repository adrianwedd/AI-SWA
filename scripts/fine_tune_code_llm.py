"""Fine-tune a lightweight code LLM on repository patches."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from git import Repo


def collect_patches(repo_path: Path, max_commits: int = 100) -> List[str]:
    """Return ``max_commits`` most recent commit patches."""
    repo = Repo(repo_path)
    patches = []
    for commit in repo.iter_commits("HEAD", max_count=max_commits):
        patches.append(repo.git.show(commit.hexsha, format="", patches=True))
    return patches


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Directory for fine-tuned model")
    parser.add_argument("--commits", type=int, default=100)
    parser.add_argument("--model", default="distilgpt2")
    args = parser.parse_args()

    patches = collect_patches(Path.cwd(), args.commits)

    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        Trainer,
        TrainingArguments,
        DataCollatorForLanguageModeling,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model)

    encodings = tokenizer(patches, truncation=True, padding=True)
    class PatchDataset:
        def __init__(self, encs):
            self.encs = encs
        def __len__(self):
            return len(self.encs["input_ids"])
        def __getitem__(self, idx):
            item = {k: v[idx] for k, v in self.encs.items()}
            item["labels"] = item["input_ids"]
            return item

    dataset = PatchDataset(encodings)
    args_train = TrainingArguments(output_dir=str(args.output), num_train_epochs=1, per_device_train_batch_size=1)
    trainer = Trainer(
        model=model,
        args=args_train,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
        train_dataset=dataset,
    )
    trainer.train()
    trainer.save_model(str(args.output))


if __name__ == "__main__":  # pragma: no cover - CLI
    main()
