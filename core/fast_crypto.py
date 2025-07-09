"""Optional Rust-backed cryptography helpers."""

from __future__ import annotations

try:
    from rust_ext import hmac_sha256_base64  # type: ignore
except Exception:  # pragma: no cover - fallback when extension missing
    import base64
    import hashlib
    import hmac

    def hmac_sha256_base64(key: str, data: bytes | str) -> str:
        """Return base64-encoded HMAC-SHA256 digest."""
        if isinstance(data, str):
            data_bytes = data.encode()
        else:
            data_bytes = data
        digest = hmac.new(key.encode(), data_bytes, hashlib.sha256).digest()
        return base64.b64encode(digest).decode()
