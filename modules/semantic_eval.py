"""Sentence-BERT based conceptual similarity evaluation."""
from __future__ import annotations
from typing import Any
import numpy as np
from config import MODEL_CACHE_DIR, SENTENCE_MODEL

_MODEL: Any | None = None


def load_model(model_name: str = SENTENCE_MODEL) -> Any:
    global _MODEL
    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
            # The model is pre-fetched on first setup.  Offline mode prevents
            # every analysis from making an unnecessary hub metadata request.
            _MODEL = SentenceTransformer(
                model_name, cache_folder=str(MODEL_CACHE_DIR), local_files_only=True
            )
        except Exception as exc:
            raise RuntimeError("Unable to load the semantic model. Check internet access and dependencies.") from exc
    return _MODEL


def semantic_similarity(transcript: str, reference: str) -> float:
    """Return cosine similarity as a bounded 0–100 percentage."""
    if not transcript.strip() or not reference.strip():
        raise ValueError("Transcript and reference explanation cannot be empty.")
    embeddings = np.asarray(load_model().encode([transcript, reference], normalize_embeddings=True))
    return round(float(np.clip(np.dot(embeddings[0], embeddings[1]), 0.0, 1.0)) * 100, 2)
