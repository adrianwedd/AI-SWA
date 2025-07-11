# CI Test Review

A local run of the test suite exposed failures related to missing test dependencies:

```
E   RuntimeError: The starlette.testclient module requires the httpx package to be installed.
```

The `tests/test_broker_api.py` import `fastapi.testclient` which depends on `httpx`. This package was missing from `requirements.txt`, causing the suite to fail. `httpx` has now been added and a `--run-integration` flag was introduced so network intensive tests only run when explicitly requested.
