# Dynamic Configuration Reload

SelfArchitectAI services watch `config.yaml` for changes using `core.config.reload_config()`.
Send a `SIGHUP` signal to any service to trigger a reload without restarting.

## Usage

1. Edit `config.yaml` with new settings.
2. Run `kill -HUP <pid>` for the target service.
3. The service reloads the file and applies the updated values.

Only file modifications and environment variable overrides are supported.
