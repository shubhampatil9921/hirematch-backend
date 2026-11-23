
import pytest

from app.ml.experience_matcher import ExperienceMatcher


@pytest.fixture
def matcher():
    return ExperienceMatcher()


def test_candidate_meets_requirement(matcher):
    result = matcher.calculate_experience_match(5, 3)

    assert result["meets_requirement"] is True
    assert result["experience_score"] == 100.0
    assert result["experience_gap"] == 0


def test_candidate_exactly_meets_requirement(matcher):
    result = matcher.calculate_experience_match(3, 3)

    assert result["meets_requirement"] is True
    assert result["experience_score"] == 100.0


def test_candidate_below_requirement(matcher):
    result = matcher.calculate_experience_match(1, 3)

    assert result["meets_requirement"] is False
    assert result["experience_score"] == 33.33
    assert result["experience_gap"] == 2


def test_zero_experience_requirement(matcher):
    result = matcher.calculate_experience_match(2, 0)

    assert result["meets_requirement"] is True
    assert result["experience_score"] == 100.0


def test_zero_candidate_experience(matcher):
    result = matcher.calculate_experience_match(0, 3)

    assert result["meets_requirement"] is False
    assert result["experience_score"] == 0.0


def test_negative_candidate_experience(matcher):
    with pytest.raises(ValueError):
        matcher.calculate_experience_match(-1, 3)


def test_negative_required_experience(matcher):
    with pytest.raises(ValueError):
        matcher.calculate_experience_match(3, -1)


def test_none_candidate_experience(matcher):
    with pytest.raises(ValueError):
        matcher.calculate_experience_match(None, 3)


def test_none_required_experience(matcher):
    with pytest.raises(ValueError):
        matcher.calculate_experience_match(3, None)
