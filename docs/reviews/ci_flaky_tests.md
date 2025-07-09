# CI Test Review

A local run of the test suite exposed failures related to missing test dependencies:

```
E   RuntimeError: The starlette.testclient module requires the httpx package to be installed.
```

The `tests/test_broker_api.py` import `fastapi.testclient` which depends on `httpx`. This package is not listed in `requirements.txt`, causing the suite to fail. Adding `httpx` to the development dependencies or vendor tests can resolve this issue.
