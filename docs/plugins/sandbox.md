# Plugin Sandbox Environment

The CI pipeline executes plugin unit tests inside a restricted Docker container to
catch malicious behavior early. The sandbox is defined by
`plugins/sandbox/Dockerfile` and uses a minimal Python base image.

Key properties:

- Dependencies from `requirements.lock` are installed during the build.
- A non‑root `sandbox` user runs all tests.
- The container itself has no network access and a read‑only file system when run
  in CI (`--network none` and `--read-only`).
- Temporary write access is provided only through an in-memory `/tmp` volume.

If a plugin attempts to access the network or modify the repository, the tests
fail and the pipeline aborts.
