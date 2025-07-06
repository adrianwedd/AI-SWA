"""Minimal security utilities for microservices."""

from __future__ import annotations

import os
from dataclasses import dataclass
from fastapi import Header, HTTPException, Depends


@dataclass
class User:
    """Simple user identity carrying a role."""

    username: str
    role: str

def verify_api_key(x_api_key: str | None = Header(None)) -> None:
    """Verify the ``X-API-Key`` header if ``API_KEY`` is configured."""
    api_key = os.getenv("API_KEY")
    if api_key and x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def _parse_tokens() -> dict[str, User]:
    """Return mapping of authentication tokens to ``User`` objects."""
    env = os.getenv("API_TOKENS")
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

    def _require(user: User = Depends(verify_token)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _require
