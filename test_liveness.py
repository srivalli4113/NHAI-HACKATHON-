import numpy as np

from ai.liveness import LivenessEngine


def test_liveness_contract():
    image = np.full((160, 160, 3), 120, dtype=np.uint8)
    result = LivenessEngine().evaluate(image)
    assert result.status in {"Live", "Fake", "Suspicious"}
    assert 0 <= result.score <= 1

