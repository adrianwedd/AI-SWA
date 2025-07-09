"""Minimal security utilities for microservices."""

from __future__ import annotations

import json
from dataclasses import dataclass
from fastapi import Header, HTTPException, Depends, Request
from .config import load_config


@dataclass
class User:
    """Simple user identity carrying a role."""

    username: str
    role: str

def verify_api_key(x_api_key: str | None = Header(None)) -> None:
    """Verify the ``X-API-Key`` header if an API key is configured."""
    api_key = load_config()["security"].get("api_key")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def _parse_tokens() -> dict[str, User]:
    """Return mapping of authentication tokens to ``User`` objects."""
    env = load_config()["security"].get("api_tokens")
    if not env:
        return {}
    tokens: dict[str, User] = {}
    for item in env.split(","):
        try:
            token, username, role = item.split(":")
        except ValueError:
            continue
        tokens[token.strip()] = User(username=username.strip(), role=role.strip())
    return tokens


def verify_token(authorization: str | None = Header(None)) -> User:
    """Validate ``Authorization`` header and return the requesting user."""
    tokens = _parse_tokens()
    if not tokens:
        # No tokens configured -> allow anonymous access for tests
        return User(username="anonymous", role="admin")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ", 1)[1]
    user = tokens.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def require_role(roles: list[str]):
    """FastAPI dependency ensuring the user has one of ``roles``."""

    def _require(request: Request, authorization: str | None = Header(None)) -> User:
        user = getattr(request.state, "user", None)
        if user is None:
            user = verify_token(authorization)
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _require

ALLOWED_PLUGIN_PERMISSIONS = {"read_files", "network"}


def validate_plugin_permissions(perms: list[str]) -> None:
    """Ensure all plugin permissions are allowed."""
    for perm in perms:
        if perm not in ALLOWED_PLUGIN_PERMISSIONS:
            raise ValueError(f"Permission '{perm}' not allowed")


def verify_plugin_signature(manifest: dict, signature: str) -> None:
    """Verify plugin manifest signature if signing key is configured."""
    key = load_config()["security"].get("plugin_signing_key")
    if not key:
        return
    import hmac
    from .fast_crypto import hmac_sha256_base64

    payload = json.dumps(manifest, sort_keys=True)
    expected = hmac_sha256_base64(key, payload)
    if not hmac.compare_digest(signature, expected):
        raise ValueError("Invalid plugin signature")

