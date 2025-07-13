from grafanalib.core import Dashboard, Graph, Row, Target

OBSERVER_DASHBOARD = Dashboard(
    title="Observer Metrics",
    rows=[
        Row(panels=[
            Graph(
                title="Worker CPU Usage",
                dataSource="Prometheus",
                targets=[Target(expr="process_cpu_seconds_total", legendFormat="cpu")],
            ),
            Graph(
                title="Worker Memory",
                dataSource="Prometheus",
                targets=[Target(expr="process_resident_memory_bytes", legendFormat="mem")],
            ),
        ]),
        Row(panels=[
            Graph(
                title="Tasks Executed",
                dataSource="Prometheus",
                targets=[Target(expr="tasks_executed_total", legendFormat="executed")],
            ),
            Graph(
                title="Orchestrator Runs",
                dataSource="Prometheus",
                targets=[Target(expr="orchestrator_runs_total", legendFormat="runs")],
            ),
        ]),
    ],
).auto_panel_ids()

if __name__ == "__main__":
    import json
    import logging

    from core.log_utils import configure_logging

    configure_logging()
    logging.info(json.dumps(OBSERVER_DASHBOARD.to_json_data(), indent=2))
