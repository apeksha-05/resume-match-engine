import uuid

import pytest
from pydantic import ValidationError

from app.schemas.recommendation import RecommendationRequest


def test_minimal_request_uses_defaults():
    request = RecommendationRequest(resume_id=uuid.uuid4())

    assert request.limit == 10
    assert request.search is None
    assert request.work_mode is None
    assert request.max_years is None


def test_accepts_all_filters():
    request = RecommendationRequest(
        resume_id=uuid.uuid4(),
        search="python",
        work_mode="remote",
        max_years=2,
        limit=20,
    )

    assert request.work_mode == "remote"
    assert request.max_years == 2


def test_rejects_unknown_work_mode():
    with pytest.raises(ValidationError):
        RecommendationRequest(resume_id=uuid.uuid4(), work_mode="flexible")


@pytest.mark.parametrize("limit", [0, 51, 1000])
def test_rejects_limit_out_of_range(limit: int):
    with pytest.raises(ValidationError):
        RecommendationRequest(resume_id=uuid.uuid4(), limit=limit)


def test_rejects_negative_max_years():
    with pytest.raises(ValidationError):
        RecommendationRequest(resume_id=uuid.uuid4(), max_years=-1)


def test_rejects_overlong_search():
    with pytest.raises(ValidationError):
        RecommendationRequest(resume_id=uuid.uuid4(), search="x" * 101)