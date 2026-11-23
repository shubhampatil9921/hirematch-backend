
import numpy as np

from app.ml.semantic_skill_matcher import SemanticSkillMatcher


class FakeEmbeddingModel:
    def encode(self, skills, **kwargs):
        vectors = {
            "python": [1.0, 0.0],
            "accounting": [0.0, 1.0],
        }

        return np.array([vectors[skill] for skill in skills])


class FakeESCOVocabulary:
    """Simulates unambiguous ESCO concept resolution."""

    concepts = {
        "natural language processing": {
            "uri": "esco:nlp",
            "preferred_label": "natural language processing",
        },
        "nlp": {
            "uri": "esco:nlp",
            "preferred_label": "natural language processing",
        },
    }

    def resolve(self, skill):
        return self.concepts.get(skill.lower())


def test_esco_equivalent_skills_match():
    matcher = SemanticSkillMatcher(
        model=FakeEmbeddingModel(),
        esco_vocabulary=FakeESCOVocabulary()
    )

    result = matcher.calculate_skill_match(
        ["NLP"],
        ["Natural Language Processing"]
    )

    assert result["exact_match_count"] == 1
    assert result["semantic_match_count"] == 0
    assert result["skill_coverage"] == 100.0


def test_manual_alias_takes_priority_over_esco():
    matcher = SemanticSkillMatcher(
        model=FakeEmbeddingModel(),
        esco_vocabulary=FakeESCOVocabulary()
    )

    result = matcher.calculate_skill_match(
        ["ML"],
        ["Machine Learning"]
    )

    assert result["exact_match_count"] == 1
    assert result["skill_coverage"] == 100.0


def test_unresolved_skill_falls_back_to_normalized_text():
    matcher = SemanticSkillMatcher(
        model=FakeEmbeddingModel(),
        esco_vocabulary=FakeESCOVocabulary()
    )

    result = matcher.calculate_skill_match(
        ["Python"],
        ["Accounting"]
    )

    assert result["matched_count"] == 0
    assert result["missing_skills"] == ["Accounting"]
