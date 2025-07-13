from grafanalib.core import Dashboard, Graph, Row, Target

DASHBOARD = Dashboard(
    title="Community Health",
    rows=[
        Row(panels=[
            Graph(
                title="Time to First Response",
                dataSource="Prometheus",
                targets=[Target(expr="chaoss_time_to_first_response", legendFormat="hours")],
            ),
            Graph(
                title="Contributor Absence Factor",
                dataSource="Prometheus",
                targets=[Target(expr="chaoss_contributor_absence_factor", legendFormat="factor")],
            ),
        ])
    ],
).auto_panel_ids()

if __name__ == "__main__":
    import json
    import logging

    from core.log_utils import configure_logging

    configure_logging()
    logging.info(json.dumps(DASHBOARD.to_json_data(), indent=2))
