import numpy as np
import pytest

from app.models.resume import EMBEDDING_DIM
from app.services.embedding_service import cosine_similarity, embed_texts


def test_no_texts_gives_no_vectors():
    assert embed_texts([]) == []


def test_vectors_match_the_database_column_size():
    vectors = embed_texts(["Built REST APIs in Python"])

    assert len(vectors) == 1
    assert len(vectors[0]) == EMBEDDING_DIM


def test_similar_sentences_score_higher_than_unrelated_ones():
    api, services, bread = embed_texts(
        [
            "Built REST APIs in Python",
            "Developed web services using Python",
            "Baked sourdough bread every morning",
        ]
    )

    assert cosine_similarity(api, services) > cosine_similarity(api, bread)


def test_the_same_text_always_gives_the_same_vector():
    first = embed_texts(["Wrote unit tests with pytest"])[0]
    second = embed_texts(["Wrote unit tests with pytest"])[0]

    assert np.allclose(first, second)


def test_a_vector_is_identical_to_itself():
    vector = embed_texts(["Docker and Kubernetes"])[0]

    assert cosine_similarity(vector, vector) == pytest.approx(1.0)


def test_a_zero_vector_has_no_similarity():
    assert cosine_similarity([0.0, 0.0, 0.0], [1.0, 2.0, 3.0]) == 0.0
