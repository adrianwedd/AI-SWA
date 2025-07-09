"""Repository-wide configuration helper."""

from core.config import load_config as _load_config

__all__ = ["load_config"]


def load_config(path=None):
    """Return configuration merged with environment overrides.

    Parameters
    ----------
    path : str | Path | None, optional
        Optional path to a YAML configuration file. When omitted the
        ``CONFIG_FILE`` environment variable or ``config.yaml`` will be used.
    """
    return _load_config(path)

