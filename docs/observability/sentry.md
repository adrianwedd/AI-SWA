# Sentry Error Monitoring

SelfArchitectAI services can report runtime errors to Sentry. Set the `SENTRY_DSN` environment variable for each service to enable the integration.

## Setup

1. Install dependencies via `pip install -r requirements.lock`.
2. Provide your project DSN in `SENTRY_DSN` for `core/bootstrap.py`, `broker/main.py` and `worker/main.py`.
3. Start the services as usual. If the variable is unset, Sentry is disabled.

Example:
```bash
export SENTRY_DSN=https://<key>@sentry.io/<project>
python core/bootstrap.py
```
