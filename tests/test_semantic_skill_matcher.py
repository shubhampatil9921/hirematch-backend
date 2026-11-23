
import numpy as np
import pytest

from app.ml.semantic_skill_matcher import SemanticSkillMatcher


class FakeEmbeddingModel:
    """Small deterministic encoder for unit tests."""

    vectors = {
        "data analysis": [1.0, 0.0, 0.0],
        "data analytics": [0.95, 0.312, 0.0],
        "business intelligence": [0.6, 0.8, 0.0],
        "python": [0.0, 1.0, 0.0],
        "accounting": [0.0, 0.0, 1.0],
    }

    def encode(self, skills, **kwargs):
        return np.array([
            self.vectors[skill]
            for skill in skills
        ])


@pytest.fixture
def matcher():
    return SemanticSkillMatcher(
        threshold=0.82,
        model=FakeEmbeddingModel()
    )


def test_semantic_match(matcher):
    result = matcher.calculate_skill_match(
        ["Data Analysis"],
        ["Data Analytics"]
    )

    assert result["semantic_match_count"] == 1
    assert result["exact_match_count"] == 0
    assert result["skill_coverage"] == 100.0


def test_exact_match(matcher):
    result = matcher.calculate_skill_match(
        ["Python"],
        ["Python"]
    )

    assert result["exact_match_count"] == 1
    assert result["semantic_match_count"] == 0


def test_unrelated_skills_do_not_match(matcher):
    result = matcher.calculate_skill_match(
        ["Python"],
        ["Accounting"]
    )

    assert result["matched_count"] == 0
    assert result["missing_skills"] == ["Accounting"]


def test_one_resume_skill_is_not_reused(matcher):
    result = matcher.calculate_skill_match(
        ["Data Analysis"],
        ["Data Analytics", "Business Intelligence"]
    )

    assert result["semantic_match_count"] == 1
    assert result["matched_count"] == 1
    assert result["missing_skills"] == ["Business Intelligence"]


def test_empty_job_skills(matcher):
    result = matcher.calculate_skill_match(
        ["Python"],
        []
    )

    assert result["total_required_skills"] == 0
    assert result["skill_coverage"] == 0.0


def test_invalid_input(matcher):
    with pytest.raises(ValueError):
        matcher.calculate_skill_match("Python", ["ML"])
