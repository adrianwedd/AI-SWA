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
    print(json.dumps(DASHBOARD.to_json_data(), indent=2))
