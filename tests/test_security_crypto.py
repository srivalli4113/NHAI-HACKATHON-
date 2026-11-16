import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.security.auth import hash_password, verify_password
from app.security.crypto import decrypt_embedding, encrypt_embedding


def test_password_hash_verification():
    stored = hash_password("secret")
    assert verify_password("secret", stored)
    assert not verify_password("wrong", stored)


def test_embedding_encryption_round_trip():
    vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)
    restored = decrypt_embedding(encrypt_embedding(vector))
    assert np.allclose(vector, restored)

