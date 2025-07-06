import yaml
from pathlib import Path


def main(path="tasks.yml"):
    p = Path(path)
    text = p.read_text()
    lines = text.splitlines()
    header = []
    i = 0
    while i < len(lines) and lines[i].startswith("#"):
        header.append(lines[i])
        i += 1
    tasks = yaml.safe_load("\n".join(lines[i:])) or []

    for t in tasks:
        if "area" not in t and "component" in t:
            t["area"] = t.pop("component")
        if "actionable_steps" not in t:
            t["actionable_steps"] = []
        if "acceptance_criteria" not in t:
            t["acceptance_criteria"] = []
        if "assigned_to" not in t:
            t["assigned_to"] = None
        if "epic" not in t:
            t["epic"] = "Legacy"
    with p.open("w") as fh:
        if header:
            fh.write("\n".join(header) + "\n")
        yaml.safe_dump(tasks, fh, sort_keys=False)


if __name__ == "__main__":
    main()
