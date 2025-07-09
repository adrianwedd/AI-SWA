"""Generate Grafana dashboard JSON files."""

from pathlib import Path
import json
from grafanalib._gen import DashboardEncoder

from grafana.dashboard import DASHBOARD
from grafana.observer_dashboard import OBSERVER_DASHBOARD
from grafana.rl_training_dashboard import RL_TRAINING_DASHBOARD


def write_dashboard(obj, path: Path) -> None:
    path.write_text(json.dumps(obj.to_json_data(), indent=2, cls=DashboardEncoder))


OUTPUT_DIR = Path("grafana/dashboards")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_dashboard(DASHBOARD, OUTPUT_DIR / "improvement-dashboard.json")
    write_dashboard(OBSERVER_DASHBOARD, OUTPUT_DIR / "observer-dashboard.json")
    write_dashboard(RL_TRAINING_DASHBOARD, OUTPUT_DIR / "rl_training.json")
    print("Dashboards updated")


if __name__ == "__main__":
    main()

