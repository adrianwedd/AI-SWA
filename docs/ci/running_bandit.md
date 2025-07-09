# Running Bandit Locally

The CI workflow uses [Bandit](https://bandit.readthedocs.io) to scan the source code for security issues. To reproduce the scan locally:

1. Install the dependencies from the lock file:
   ```bash
   pip install -r requirements.lock
   ```
2. Run Bandit from the project root:
   ```bash
   bandit -r core plugins -x tests -f json -o bandit.json
   ```
3. Review the `bandit.json` report. The CI job fails if any findings with `issue_severity` set to `HIGH` are present.
