"""Generate Grafana dashboard JSON files."""

from pathlib import Path
import json

from grafana.dashboard import DASHBOARD
from grafana.observer_dashboard import OBSERVER_DASHBOARD


def write_dashboard(obj, path: Path) -> None:
    path.write_text(json.dumps(obj.to_json_data(), indent=2))


def main() -> None:
    write_dashboard(DASHBOARD, Path("improvement-dashboard.json"))
    write_dashboard(OBSERVER_DASHBOARD, Path("observer-dashboard.json"))
    print("Dashboards updated")


if __name__ == "__main__":
    main()

