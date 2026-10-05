"""Local, free semantic embeddings using sentence-transformers.
No API key or internet access needed after the model's first download.
"""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"  # 384-dimensional, matches our pgvector columns


@lru_cache
def _get_model() -> SentenceTransformer:
    # Cached so the (relatively slow) model load happens only once per process.
    return SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Returns one normalized embedding vector per input string."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    a = np.array(vector_a)
    b = np.array(vector_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)