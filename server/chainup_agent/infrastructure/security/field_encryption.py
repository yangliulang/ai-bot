"""Fernet at-rest payloads; key env ``CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY``."""

from __future__ import annotations

import json

from cryptography.fernet import Fernet, InvalidToken


def encrypt_json_plaintext(plaintext_key: bytes, payload: dict[str, str]) -> bytes:
    """JSON-encode mapping and Fernet-seal."""
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    f = Fernet(plaintext_key)
    return f.encrypt(raw)


def decrypt_json_plaintext(plaintext_key: bytes, token: bytes) -> dict[str, str]:
    f = Fernet(plaintext_key)
    try:
        raw = f.decrypt(token)
    except InvalidToken as e:
        msg = "Sealed credential payload corrupted or encrypted with another key"
        raise ValueError(msg) from e
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        msg = "Invalid sealed payload shape"
        raise ValueError(msg)
    out: dict[str, str] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str):
            out[k] = v
        else:
            msg = "Invalid sealed payload entries"
            raise ValueError(msg)
    return out
