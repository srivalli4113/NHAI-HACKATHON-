import base64
import hashlib
import json
from typing import Any

import numpy as np
from cryptography.fernet import Fernet

from app.core.config import get_settings


def _fernet() -> Fernet:
    secret = get_settings().app_secret_key.encode("utf-8")
    digest = hashlib.sha256(secret).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_json(payload: dict[str, Any]) -> bytes:
    return _fernet().encrypt(json.dumps(payload, separators=(",", ":")).encode("utf-8"))


def decrypt_json(blob: bytes) -> dict[str, Any]:
    return json.loads(_fernet().decrypt(blob).decode("utf-8"))


def encrypt_embedding(vector: np.ndarray) -> bytes:
    arr = vector.astype(np.float32)
    return encrypt_json({"shape": arr.shape, "values": arr.tolist()})


def decrypt_embedding(blob: bytes) -> np.ndarray:
    payload = decrypt_json(blob)
    return np.array(payload["values"], dtype=np.float32).reshape(payload["shape"])

