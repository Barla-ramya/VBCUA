import numpy as np
from modules import semantic_eval


class FakeModel:
    def encode(self, _items, normalize_embeddings=True):
        return np.array([[1., 0.], [1., 0.]])


def test_semantic_score_with_cached_model(monkeypatch) -> None:
    monkeypatch.setattr(semantic_eval, "_MODEL", FakeModel())
    assert semantic_eval.semantic_similarity("a concept", "a reference") == 100.0
