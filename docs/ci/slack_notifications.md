# Slack Notification Format

The GitHub Actions workflows send a message to Slack when a job finishes.

Set a repository secret named `SLACK_WEBHOOK_URL` containing an incoming webhook URL for your workspace. Each workflow posts one of the following JSON payloads:

```json
{"text": "CI succeeded for <owner>/<repo> at <sha>"}
```

```json
{"text": "CI failed for <owner>/<repo> at <sha>"}
```

Replace `<owner>/<repo>` with the repository slug and `<sha>` with the commit hash. The same format applies to other workflows like release and Grafana dashboard deployment.
