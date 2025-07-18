from grafanalib.core import Dashboard, Graph, Row, Target

RL_TRAINING_DASHBOARD = Dashboard(
    title="RL Training Metrics",
    rows=[
        Row(panels=[
            Graph(
                title="Episode Reward",
                dataSource="Prometheus",
                targets=[Target(expr="rl_training_reward", legendFormat="reward")],
            ),
            Graph(
                title="Episode Length",
                dataSource="Prometheus",
                targets=[Target(expr="rl_training_episode_length", legendFormat="steps")],
            ),
        ])
    ],
).auto_panel_ids()

if __name__ == "__main__":
    import json
    import logging
    from grafanalib._gen import DashboardEncoder

    from core.log_utils import configure_logging

    configure_logging()
    logging.info(
        json.dumps(RL_TRAINING_DASHBOARD.to_json_data(), indent=2, cls=DashboardEncoder)
    )
