# Continuous Integration Overview

This repository uses GitHub Actions to enforce quality gates on every commit. The workflow performs dependency audits, linting, tests, and security scans.

## Node Security Check

Node-based services run an additional step that installs dependencies and executes `npm audit --production`. The audit fails the build if any vulnerabilities of **high** severity or greater are reported.

Run the check locally from the project root:

```bash
cd services/node
npm ci --omit=dev
npm audit --production --audit-level=high
```

