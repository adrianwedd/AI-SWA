from __future__ import annotations

import json
from typing import Any

from ariadne import QueryType, make_executable_schema, gql
from ariadne.asgi import GraphQL

from .service import list_plugins_from_db, get_db


type_defs = gql(
    """
    type Plugin {
        id: String!
        name: String!
        version: String!
        dependencies: [String!]!
        downloadUrl: String!
    }

    type Query {
        plugins: [Plugin!]!
        plugin(id: String!): Plugin
    }
    """
)

query = QueryType()


@query.field("plugins")
def resolve_plugins(*_: Any) -> list[dict[str, Any]]:
    plugins = []
    for row in list_plugins_from_db():
        deps = json.loads(row.get("dependencies", "[]")) if row.get("dependencies") else []
        plugins.append(
            {
                "id": row["id"],
                "name": row["name"],
                "version": row["version"],
                "dependencies": deps,
                "downloadUrl": f"/plugins/{row['id']}/download",
            }
        )
    return plugins


@query.field("plugin")
def resolve_plugin(*_: Any, id: str) -> dict[str, Any] | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM plugins WHERE id=?", (id,)).fetchone()
    conn.close()
    if not row:
        return None
    deps = json.loads(row["dependencies"]) if row["dependencies"] else []
    return {
        "id": row["id"],
        "name": row["name"],
        "version": row["version"],
        "dependencies": deps,
        "downloadUrl": f"/plugins/{row['id']}/download",
    }


schema = make_executable_schema(type_defs, query)
app = GraphQL(schema)

