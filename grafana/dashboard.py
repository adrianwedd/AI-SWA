from grafanalib.core import Dashboard, Graph, Row, Target

DASHBOARD = Dashboard(
    title="SelfArchitectAI Overview",
    rows=[
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
            Graph(
                title="Average Task Duration",
                dataSource="Prometheus",
                targets=[
                    Target(
                        expr="rate(task_duration_seconds_sum[1m]) / rate(task_duration_seconds_count[1m])",
                        legendFormat="seconds",
                    )
                ],
            ),
        ])
    ],
).auto_panel_ids()

if __name__ == "__main__":
    import json
    print(json.dumps(DASHBOARD.to_json_data(), indent=2))
