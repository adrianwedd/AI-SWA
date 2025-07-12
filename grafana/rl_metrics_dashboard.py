from grafanalib.core import Dashboard, Graph, Row, Target

RL_METRICS_DASHBOARD = Dashboard(
    title="RL Episode Metrics",
    rows=[
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
        ])
    ],
).auto_panel_ids()

if __name__ == "__main__":
    import json
    from grafanalib._gen import DashboardEncoder

    print(json.dumps(RL_METRICS_DASHBOARD.to_json_data(), indent=2, cls=DashboardEncoder))
