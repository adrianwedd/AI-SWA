# Plugin Marketplace GraphQL API

The marketplace exposes a small GraphQL schema for retrieving available plugins and their download links. It mirrors the REST and gRPC interfaces provided by `service.py`.

```graphql
# Schema Definition Language

type Plugin {
    id: String!
    name: String!
    version: String!
    dependencies: [String!]!
    downloadUrl: String!
}

type Query {
    # List all plugins in the marketplace
    plugins: [Plugin!]!

    # Retrieve a single plugin by its ID
    plugin(id: String!): Plugin
}
```

Query the endpoint with standard GraphQL POST requests. Each `Plugin` includes a `downloadUrl` matching the REST endpoint `/plugins/<id>/download`.

