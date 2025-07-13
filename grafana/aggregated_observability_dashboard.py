from grafanalib.core import Dashboard, Graph, Row, Target

OBSERVABILITY_METRICS_DASHBOARD = Dashboard(
    title="Aggregated Observability Metrics",
    rows=[
        Row(panels=[
            Graph(
                title="Tasks Executed",
                dataSource="Prometheus",
                targets=[Target(expr="tasks_executed_total", legendFormat="tasks")],
            ),
            Graph(
                title="Orchestrator Runs",
                dataSource="Prometheus",
                targets=[Target(expr="orchestrator_runs_total", legendFormat="runs")],
            ),
            Graph(
                title="Plugin Downloads",
                dataSource="Prometheus",
                targets=[Target(expr="plugin_downloads_total", legendFormat="downloads")],
            ),
        ]),
        Row(panels=[
            Graph(
                title="Episode Reward Average",
                dataSource="Prometheus",
                targets=[Target(expr="rate(rl_training_reward_summary_sum[1m]) / rate(rl_training_reward_summary_count[1m])", legendFormat="avg reward")],
            ),
            Graph(
                title="Episode Length Average",
                dataSource="Prometheus",
                targets=[Target(expr="rate(rl_training_episode_length_summary_sum[1m]) / rate(rl_training_episode_length_summary_count[1m])", legendFormat="avg length")],
            ),
            Graph(
                title="Episodes Processed",
                dataSource="Prometheus",
                targets=[Target(expr="rl_training_episodes_total", legendFormat="episodes")],
            ),
        ]),
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
    ],
).auto_panel_ids()

if __name__ == "__main__":
    import json
    import logging
    from grafanalib._gen import DashboardEncoder

    from core.log_utils import configure_logging

    configure_logging()
    logging.info(
        json.dumps(
            OBSERVABILITY_METRICS_DASHBOARD.to_json_data(),
            indent=2,
            cls=DashboardEncoder,
        )
    )
