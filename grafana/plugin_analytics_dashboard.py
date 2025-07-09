from grafanalib.core import Dashboard, Graph, Row, Target

PLUGIN_ANALYTICS_DASHBOARD = Dashboard(
    title="Plugin Analytics",
    rows=[
        Row(panels=[
            Graph(
                title="Plugin Downloads",
                dataSource="Prometheus",
                targets=[Target(expr="plugin_downloads_total", legendFormat="downloads")],
            ),
            Graph(
                title="Search Queries",
                dataSource="Prometheus",
                targets=[Target(expr="plugin_search_queries_total", legendFormat="queries")],
            ),
            Graph(
                title="Ratings Submitted",
                dataSource="Prometheus",
                targets=[Target(expr="plugin_ratings_total", legendFormat="ratings")],
            ),
        ])
    ],
).auto_panel_ids()

if __name__ == "__main__":
    import json
    from grafanalib._gen import DashboardEncoder

    print(json.dumps(PLUGIN_ANALYTICS_DASHBOARD.to_json_data(), indent=2, cls=DashboardEncoder))
