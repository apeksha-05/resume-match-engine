"""Local, free semantic embeddings.

The all-MiniLM-L6-v2 model runs through ONNX Runtime (via fastembed), so the
application does not need PyTorch. No API key or internet access is needed
after the model's first download.
"""

from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding

from app.core.config import get_settings

# 384 dimensions, which matches the pgvector columns in the database.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache
def _get_model() -> TextEmbedding:
    # Cached so the (relatively slow) model load happens only once per process.
    cache_dir = get_settings().embedding_cache_dir or None
    return TextEmbedding(model_name=MODEL_NAME, cache_dir=cache_dir)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Returns one embedding vector per input string."""
    if not texts:
        return []
    return [vector.tolist() for vector in _get_model().embed(texts)]


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)
    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator == 0:
        return 0.0
    return float(np.dot(a, b) / denominator)
