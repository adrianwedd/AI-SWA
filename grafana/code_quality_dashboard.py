from grafanalib.core import Dashboard, Graph, Row, Target

CODE_QUALITY_DASHBOARD = Dashboard(
    title="Code Quality and Tests",
    rows=[
        Row(panels=[
            Graph(
                title="Average Complexity",
                dataSource="Prometheus",
                targets=[Target(expr="code_complexity_average", legendFormat="avg")],
            ),
            Graph(
                title="Maintainability Index",
                dataSource="Prometheus",
                targets=[Target(expr="maintainability_index", legendFormat="mi")],
            ),
            Graph(
                title="Test Coverage",
                dataSource="Prometheus",
                targets=[Target(expr="test_coverage_percent", legendFormat="pct")],
            ),
        ]),
        Row(panels=[
            Graph(
                title="Test Failures",
                dataSource="Prometheus",
                targets=[Target(expr="tests_failed_total", legendFormat="failures")],
            ),
            Graph(
                title="Tests Executed",
                dataSource="Prometheus",
                targets=[Target(expr="tests_executed_total", legendFormat="runs")],
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
        json.dumps(CODE_QUALITY_DASHBOARD.to_json_data(), indent=2, cls=DashboardEncoder)
    )
