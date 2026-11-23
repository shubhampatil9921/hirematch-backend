
import numpy as np

from app.ml.semantic_skill_matcher import SemanticSkillMatcher


class FakeEmbeddingModel:
    """Small deterministic model for testing without downloads."""

    def __init__(self):
        self.vectors = {
            "python": [1.0, 0.0, 0.0],
            "java": [0.0, 1.0, 0.0],
        }

    def encode(
        self,
        skills,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    ):
        return np.array([
            self.vectors[skill]
            for skill in skills
        ])


def create_matcher():
    return SemanticSkillMatcher(
        model=FakeEmbeddingModel(),
        threshold=0.82
    )


def test_verified_aliases_match_exactly():
    matcher = create_matcher()

    result = matcher.calculate_skill_match(
        resume_skills=["ML", "JavaScript"],
        job_skills=["Machine Learning", "JS", "Python"]
    )

    assert result["exact_matched_skills"] == [
        "Machine Learning",
        "JS"
    ]

    assert result["missing_skills"] == ["Python"]
    assert result["exact_match_count"] == 2
    assert result["skill_coverage"] == 66.67


def test_alias_duplicates_are_counted_once():
    matcher = create_matcher()

    result = matcher.calculate_skill_match(
        resume_skills=["ML", "Machine Learning"],
        job_skills=["Machine Learning", "ML"]
    )

    assert result["total_required_skills"] == 1
    assert result["matched_count"] == 1
    assert result["skill_coverage"] == 100.0


def test_unrelated_skills_are_not_matched_as_aliases():
    matcher = create_matcher()

    result = matcher.calculate_skill_match(
        resume_skills=["Python"],
        job_skills=["Java"]
    )

    assert result["exact_match_count"] == 0
    assert result["semantic_match_count"] == 0
    assert result["missing_skills"] == ["Java"]
    assert result["skill_coverage"] == 0.0
